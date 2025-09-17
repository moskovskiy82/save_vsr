from __future__ import annotations

import asyncio
import logging
from typing import Literal, Optional

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import (
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_SLAVE_ID,
    DEFAULT_STOPBITS,
    DEFAULT_TCP_PORT,
    TRANSPORT_SERIAL,
    TRANSPORT_TCP,

)

_LOGGER = logging.getLogger(__name__)

# How long to wait for a single Modbus operation (seconds). Increase if device is slow.
IO_TIMEOUT_S = 10.0
# Number of attempts for a single read operation before giving up
READ_ATTEMPTS = 2
# Small backoff between attempts (seconds)
READ_BACKOFF_S = 0.08


class VSRHub:
    """Manages a single Modbus connection (serial or TCP) with robust reuse."""

    def __init__(
        self,
        *,
        transport: Literal["serial", "tcp"],
        slave_id: int = DEFAULT_SLAVE_ID,
        # Serial
        port: Optional[str] = None,
        baudrate: int = DEFAULT_BAUDRATE,
        bytesize: int = DEFAULT_BYTESIZE,
        parity: str = DEFAULT_PARITY,
        stopbits: int = DEFAULT_STOPBITS,
        # TCP
        host: Optional[str] = None,
        tcp_port: int = DEFAULT_TCP_PORT,
    ) -> None:
        self.transport = transport
        self.slave_id = slave_id

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits

        self.host = host
        self.tcp_port = tcp_port

        self._client: Optional[AsyncModbusSerialClient | AsyncModbusTcpClient] = None
        self._lock = asyncio.Lock()

    async def async_connect(self) -> None:
        if self._client is not None and getattr(self._client, "connected", False):
            return
        if self.transport == TRANSPORT_SERIAL:
            self._client = AsyncModbusSerialClient(
                method="rtu",
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=IO_TIMEOUT_S,
                strict=False,  # Add this line
            )
        else:
            self._client = AsyncModbusTcpClient(
                host=self.host, port=self.tcp_port, timeout=IO_TIMEOUT_S
            )
        connected = await self._client.connect()
        if not connected:
            raise ConnectionError("Failed to connect Modbus client")

    async def async_close(self) -> None:
        if self._client is not None:
            try:
                await self._client.close()
            except Exception:  # noqa: BLE001 - best effort
                pass
            self._client = None

    async def _ensure(self) -> None:
        if self._client is None or not getattr(self._client, "connected", False):
            await self.async_connect()

    async def read_holding(self, address: int, count: int = 1) -> Optional[list[int]]:
        """
        Read holding registers (returns list[int] or None).
        Retries a small number of times to tolerate transient errors.
        """
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(READ_ATTEMPTS):
                try:
                    rr = await asyncio.wait_for(
                        self._client.read_holding_registers(address, count, slave=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    # Validate response
                    if rr is None:
                        _LOGGER.debug("Holding read returned None at %s (attempt %d)", address, attempt + 1)
                        last_exc = None
                    elif getattr(rr, "isError", lambda: False)():
                        _LOGGER.debug("Holding read isError at %s (attempt %d): %s", address, attempt + 1, rr)
                        last_exc = rr
                    else:
                        regs = getattr(rr, "registers", None)
                        if not regs:
                            _LOGGER.debug("Holding read returned empty registers at %s (attempt %d)", address, attempt + 1)
                            last_exc = None
                        else:
                            return regs
                except asyncio.TimeoutError as e:
                    _LOGGER.debug("Holding read timeout at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except ModbusException as e:
                    _LOGGER.debug("Holding read ModbusException at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except Exception as e:
                    _LOGGER.debug("Holding read exception at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e

                # Backoff before retry, short so we don't delay too much
                if attempt + 1 < READ_ATTEMPTS:
                    await asyncio.sleep(READ_BACKOFF_S)

            # All attempts failed
            _LOGGER.warning("Holding read error at %s: %s", address, last_exc)
            return None

    async def read_input(self, address: int, count: int = 1) -> Optional[list[int]]:
        """
        Read input registers (returns list[int] or None).
        Retries similar to read_holding.
        """
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(READ_ATTEMPTS):
                try:
                    rr = await asyncio.wait_for(
                        self._client.read_input_registers(address, count, slave=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    # Validate response
                    if rr is None:
                        _LOGGER.debug("Input read returned None at %s (attempt %d)", address, attempt + 1)
                        last_exc = None
                    elif getattr(rr, "isError", lambda: False)():
                        _LOGGER.debug("Input read isError at %s (attempt %d): %s", address, attempt + 1, rr)
                        last_exc = rr
                    else:
                        regs = getattr(rr, "registers", None)
                        if not regs:
                            _LOGGER.debug("Input read returned empty registers at %s (attempt %d)", address, attempt + 1)
                            last_exc = None
                        else:
                            return regs
                except asyncio.TimeoutError as e:
                    _LOGGER.debug("Input read timeout at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except ModbusException as e:
                    _LOGGER.debug("Input read ModbusException at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except Exception as e:
                    _LOGGER.debug("Input read exception at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e

                if attempt + 1 < READ_ATTEMPTS:
                    await asyncio.sleep(READ_BACKOFF_S)

            _LOGGER.warning("Input read error at %s: %s", address, last_exc)
            return None

    async def write_register(self, address: int, value: int) -> bool:
        """Write a single holding register."""
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(READ_ATTEMPTS):
                try:
                    wr = await asyncio.wait_for(
                        self._client.write_register(address, value, slave=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if wr is None:
                        _LOGGER.debug("Write register returned None at %s (attempt %d)", address, attempt + 1)
                        last_exc = None
                    elif getattr(wr, "isError", lambda: False)():
                        _LOGGER.debug("Write register isError at %s (attempt %d): %s", address, attempt + 1, wr)
                        last_exc = wr
                    else:
                        return True
                except asyncio.TimeoutError as e:
                    _LOGGER.debug("Write register timeout at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except ModbusException as e:
                    _LOGGER.debug("Write register ModbusException at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except Exception as e:
                    _LOGGER.debug("Write register exception at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e

                if attempt + 1 < READ_ATTEMPTS:
                    await asyncio.sleep(READ_BACKOFF_S)

            _LOGGER.error("Write register error at %s: %s", address, last_exc)
            return False

    async def write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil (useful if the device exposes some booleans as coils)."""
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(READ_ATTEMPTS):
                try:
                    wr = await asyncio.wait_for(
                        self._client.write_coil(address, value, slave=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if wr is None:
                        _LOGGER.debug("Write coil returned None at %s (attempt %d)", address, attempt + 1)
                        last_exc = None
                    elif getattr(wr, "isError", lambda: False)():
                        _LOGGER.debug("Write coil isError at %s (attempt %d): %s", address, attempt + 1, wr)
                        last_exc = wr
                    else:
                        return True
                except asyncio.TimeoutError as e:
                    _LOGGER.debug("Write coil timeout at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except ModbusException as e:
                    _LOGGER.debug("Write coil ModbusException at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e
                except Exception as e:
                    _LOGGER.debug("Write coil exception at %s (attempt %d): %s", address, attempt + 1, e)
                    last_exc = e

                if attempt + 1 < READ_ATTEMPTS:
                    await asyncio.sleep(READ_BACKOFF_S)

            _LOGGER.error("Write coil error at %s: %s", address, last_exc)
            return False

    @staticmethod
    def decode_uint16(regs: list[int], index: int = 0) -> int:
        try:
            return int(regs[index])
        except Exception:
            return 0

    @staticmethod
    def decode_tenth(regs: list[int], index: int = 0) -> float:
        try:
            return round(regs[index] * 0.1, 1)
        except Exception:
            return 0.0
