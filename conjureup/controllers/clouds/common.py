import asyncio

from juju.utils import run_with_interrupt

from conjureup import events
from conjureup.models.provider import LocalhostError, LocalhostJSONError


class BaseCloudController:

    cancel_monitor = asyncio.Event()

    async def _monitor_localhost(self, provider, cb):
        """ Checks that localhost/lxd is available and listening,
        updates widget accordingly
        """

        while not self.cancel_monitor.is_set():
            try:
                provider._set_lxd_dir_env()
                client_compatible = await provider.is_client_compatible()
                server_compatible = await provider.is_server_compatible()
                if client_compatible and server_compatible:
                    events.LXDAvailable.set()
                    self.cancel_monitor.set()
                    cb()
                    return
            except (LocalhostError, LocalhostJSONError, FileNotFoundError):
                pass
            await run_with_interrupt(asyncio.sleep(2),
                                     self.cancel_monitor)
