# KNX Sentinel 2

KNX Sentinel 2 is a Home Assistant add-on designed to monitor your KNX bus in real-time. It provides a visual dashboard to inspect KNX telegrams, helping you diagnose and understand your KNX traffic.

## Features

- **Real-time Monitoring**: Watch KNX telegrams as they happen on your bus.
- **Visual Dashboard**: Clean web interface to view traffic history.
- **WebSocket Streaming**: Telegrams are streamed instantly to the frontend.
- **Robust Connection**: Automatically handles connection drops and reconnections.

## Installation

1.  Add the repository URL to your Home Assistant Add-on Store:
    `https://github.com/jangoachayan/KNX-Sentinal-V2`
2.  Install **KNX Sentinel 2** from the new repository.
3.  Start the add-on.

## Configuration

The add-on requires minimal configuration as it attempts to auto-discover or use default settings.

**Note**: This add-on connects to your KNX interface/router. Ensure your Home Assistant instance has network access to your KNX IP interface.

```yaml
log_level: info
```

### Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `log_level` | Logging level (debug, info, warning, error) | `info` |

## Web Interface

Once started, click **OPEN WEB UI** to access the dashboard.
