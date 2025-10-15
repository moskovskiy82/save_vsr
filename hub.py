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

# Timeout for operations
IO_TIMEOUT_S = 10.0
# Attempts per read/write
IO_ATTEMPTS = 3
# Backoff between attempts
IO_BACKOFF_S = 0.1
# Inter-message delay for serial stability
MESSAGE_WAIT_MS = 30


class VSRHub:
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
        self._consecutive_failures = 0
        self._max_consecutive_failures = 3  # Trigger reconnect after this

    async def async_connect(self) -> None:
        await self.async_close()  # Ensure clean start
        if self.transport == TRANSPORT_SERIAL:
            self._client = AsyncModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=IO_TIMEOUT_S,
                strict=False,
            )
        else:
            self._client = AsyncModbusTcpClient(
                host=self.host, port=self.tcp_port, timeout=IO_TIMEOUT_S
            )
        connected = await self._client.connect()
        if not connected:
            raise ConnectionError("Failed to connect Modbus client")
        self._consecutive_failures = 0
        _LOGGER.debug("Modbus client connected successfully")

    async def async_close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                _LOGGER.debug("Error closing Modbus client: %s", e)
            self._client = None

    async def _ensure(self) -> None:
        if self._client is None or not self._client.connected:
            await self.async_connect()

    def _handle_failure(self, exc: Exception) -> None:
        _LOGGER.debug("Modbus operation failed: %s", exc)
        self._consecutive_failures += 1
        if self._consecutive_failures >= self._max_consecutive_failures:
            _LOGGER.warning("Too many consecutive failures; forcing reconnect")
            asyncio.create_task(self.async_connect())  # Async reconnect

    async def read_input(self, address: int, count: int = 1) -> Optional[list[int]]:
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(IO_ATTEMPTS):
                try:
                    rr = await asyncio.wait_for(
                        self._client.read_input_registers(address, count, unit=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if rr.isError():
                        raise ModbusException(f"Read input error: {rr}")
                    return rr.registers
                except (asyncio.TimeoutError, ModbusException) as e:
                    self._handle_failure(e)
                    last_exc = e
                if attempt + 1 < IO_ATTEMPTS:
                    await asyncio.sleep(IO_BACKOFF_S)
            _LOGGER.error("Failed to read input at %s after %d attempts: %s", address, IO_ATTEMPTS, last_exc)
            return None

    async def read_holding(self, address: int, count: int = 1) -> Optional[list[int]]:
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(IO_ATTEMPTS):
                try:
                    rr = await asyncio.wait_for(
                        self._client.read_holding_registers(address, count, unit=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if rr.isError():
                        raise ModbusException(f"Read holding error: {rr}")
                    return rr.registers
                except (asyncio.TimeoutError, ModbusException) as e:
                    self._handle_failure(e)
                    last_exc = e
                if attempt + 1 < IO_ATTEMPTS:
                    await asyncio.sleep(IO_BACKOFF_S)
            _LOGGER.error("Failed to read holding at %s after %d attempts: %s", address, IO_ATTEMPTS, last_exc)
            return None

    async def write_register(self, address: int, value: int) -> bool:
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(IO_ATTEMPTS):
                try:
                    wr = await asyncio.wait_for(
                        self._client.write_register(address, value, unit=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if wr.isError():
                        raise ModbusException(f"Write register error: {wr}")
                    return True
                except (asyncio.TimeoutError, ModbusException) as e:
                    self._handle_failure(e)
                    last_exc = e
                if attempt + 1 < IO_ATTEMPTS:
                    await asyncio.sleep(IO_BACKOFF_S)
            _LOGGER.error("Failed to write register at %s after %d attempts: %s", address, IO_ATTEMPTS, last_exc)
            return False

    async def write_coil(self, address: int, value: bool) -> bool:
        async with self._lock:
            await self._ensure()
            last_exc = None
            for attempt in range(IO_ATTEMPTS):
                try:
                    wr = await asyncio.wait_for(
                        self._client.write_coil(address, value, unit=self.slave_id),
                        timeout=IO_TIMEOUT_S,
                    )
                    if wr.isError():
                        raise ModbusException(f"Write coil error: {wr}")
                    return True
                except (asyncio.TimeoutError, ModbusException) as e:
                    self._handle_failure(e)
                    last_exc = e
                if attempt + 1 < IO_ATTEMPTS:
                    await asyncio.sleep(IO_BACKOFF_S)
            _LOGGER.error("Failed to write coil at %s after %d attempts: %s", address, IO_ATTEMPTS, last_exc)
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
