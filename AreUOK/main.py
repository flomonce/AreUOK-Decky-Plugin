import decky
import subprocess
import asyncio

class Plugin:
    async def _main(self):
        decky.logger.info("====== Are U OK 纯正后端已启动 ======")

    async def check_tun(self) -> bool:
        """直接让 Python 查网卡，按需触发，无轮询"""
        try:
            res = await asyncio.to_thread(
                subprocess.run,
                ["ip", "link", "show"],
                capture_output=True,
                text=True
            )
            if "tun" in res.stdout and "tunl0" not in res.stdout:
                return True
            return False
        except Exception as e:
            decky.logger.error(f"查网卡报错: {e}")
            return False
