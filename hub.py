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
                timeout=3,
            )
        else:
            self._client = AsyncModbusTcpClient(
                host=self.host, port=self.tcp_port, timeout=3
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
        async with self._lock:
            await self._ensure()
            try:
                rr = await asyncio.wait_for(
                    self._client.read_holding_registers(address, count, slave=self.slave_id),
                    timeout=3.0,
                )
                if rr is None or getattr(rr, "isError", lambda: False)():
                    _LOGGER.warning("Read holding failed at %s", address)
                    return None
                regs = getattr(rr, "registers", None)
                if not regs:
                    _LOGGER.debug("Read holding returned empty at %s", address)
                    return None
                return regs
            except (asyncio.TimeoutError, ModbusException) as e:
                _LOGGER.warning("Holding read error at %s: %s", address, e)
                return None

    async def read_input(self, address: int, count: int = 1) -> Optional[list[int]]:
        async with self._lock:
            await self._ensure()
            try:
                rr = await asyncio.wait_for(
                    self._client.read_input_registers(address, count, slave=self.slave_id),
                    timeout=3.0,
                )
                if rr is None or getattr(rr, "isError", lambda: False)():
                    _LOGGER.warning("Read input failed at %s", address)
                    return None
                regs = getattr(rr, "registers", None)
                if not regs:
                    _LOGGER.debug("Read input returned empty at %s", address)
                    return None
                return regs
            except (asyncio.TimeoutError, ModbusException) as e:
                _LOGGER.warning("Input read error at %s: %s", address, e)
                return None

    async def write_register(self, address: int, value: int) -> bool:
        async with self._lock:
            await self._ensure()
            try:
                wr = await asyncio.wait_for(
                    self._client.write_register(address, value, slave=self.slave_id),
                    timeout=3.0,
                )
                if wr is None or getattr(wr, "isError", lambda: False)():
                    _LOGGER.error("Write register failed at %s", address)
                    return False
                return True
            except (asyncio.TimeoutError, ModbusException) as e:
                _LOGGER.error("Write register error at %s: %s", address, e)
                return False

    async def write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil (useful if the device exposes some booleans as coils)."""
        async with self._lock:
            await self._ensure()
            try:
                wr = await asyncio.wait_for(
                    self._client.write_coil(address, value, slave=self.slave_id),
                    timeout=3.0,
                )
                if wr is None or getattr(wr, "isError", lambda: False)():
                    _LOGGER.error("Write coil failed at %s", address)
                    return False
                return True
            except (asyncio.TimeoutError, ModbusException) as e:
                _LOGGER.error("Write coil error at %s: %s", address, e)
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
