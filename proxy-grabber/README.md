# Proxy-Grabber
Simple http proxy grabber and checker

# Installation

```
$ pip3 install proxy-grabber
```

# Usage
``` python
from proxy_grabber import ProxyGrabber
grabber = ProxyGrabber()

# --- Grabbing proxies ---

# Parse proxy from different sources
# You can call generate_proxy_list() without arguments if you want to grab as more proxies as possible
grabber.grab_proxies(proxy_limit=100)

# --- Adding proxies ---
# Notice: you can add proxies without grabbing
# You can add some proxies from the file
grabber.load('./data/proxy.list')

# Or you can add proxy manually
grabber.add_proxies(['ip:port', 'ip:port', ...])

# --- Checking proxies ---

# [optional]
# You can specify proxy countries
grabber.set_countries(['US', 'RU', 'CA', ...])

grabber.check_proxies()

# --- Get results ---
grabber.get_proxy() # Random checked proxy
grabber.get_checked_proxies() # All checked proxies
grabber.save('./data/checked_proxies.list') # Save checked proxies to the file
```

