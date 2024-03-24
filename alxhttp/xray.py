import asyncio
from logging import Logger
import aiohttp
from aws_xray_sdk.core import patch_all, xray_recorder
from aws_xray_sdk.core.async_context import AsyncContext
from yarl import URL

_imdsv2_md_url = URL("http://169.254.169.254/latest")


async def _get_imdsv2_token(s: aiohttp.ClientSession) -> str:
    async with s.put(
        _imdsv2_md_url / "api/token",
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        timeout=3,
    ) as r:
        return await r.text()


async def get_ec2_ipv4() -> str:
    async with aiohttp.ClientSession() as s:
        token = await _get_imdsv2_token(s)

        async with s.get(
            _imdsv2_md_url / "meta-data/local-ipv4",
            headers={"X-aws-ec2-metadata-token": token},
            timeout=3,
        ) as r:
            return await r.text()


async def init_xray(log: Logger, service_name: str, daemon_port: int = 40000) -> bool:
    try:
        ec2_ipv4 = await get_ec2_ipv4()

        patch_all()
        xray_recorder.configure(
            service=service_name,
            context=AsyncContext(),
            daemon_address=f"{ec2_ipv4}:{daemon_port}",
        )
        return True
    except asyncio.TimeoutError:
        log.warning("Unable to get EC2 IP - XRay tracing disabled")
        return False
