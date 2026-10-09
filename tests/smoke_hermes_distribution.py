from pathlib import Path
from hermes_cli.plugins import discover_plugins
from gateway.platform_registry import platform_registry
from gateway.config import PlatformConfig
from hermes_constants import get_hermes_home
import json
home=get_hermes_home()
discover_plugins()
entry=platform_registry.get('softmax')
assert entry is not None, 'installed plugin not discovered'
config=PlatformConfig(enabled=True)
assert not entry.validate_config(config)
state=home/'softmax-bridge';state.mkdir()
(state/'config.json').write_text('{}')
assert entry.validate_config(config)
adapter=entry.adapter_factory(config)
assert adapter.directory==state
print(json.dumps({'discovered':entry.name,'directory':str(adapter.directory),'missing_configuration_rejected':True}))
