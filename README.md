# HTTP-HTTPS-Proxy-Server-with-Caching-in-Python

Proxy server in Python that can handle HTTP/HTTPS requests , Caching, Websites and IP blocking. It also provides logging for debugging purpose.


## Getting Started
 
The code does not uses any external networking module. It is written usinig the 'socket' moduls which comes pre-installed with python.


### Usage

After Downloading/Cloning the repo, you will need to configure the proxy settings in your web browser and you are good to go.

**For Firefox:**
* Goto Options
* Type `proxy` in the search bar and click on `Settings..` for the  `Network Proxy` tab
* Select `Manual Proxy Configuration` and enter `localhost` in HTTP Proxy and enter `8080` for the Port.
* Check `Use this proxy server for all protocols`

**For Chrome:**
* Goto Settings
* Click on `Show advanced settings...`
* Click on `Change proxy settings...`
* On the Internet Properties window, click on the `LAN settings` button
* In the LAN Settings, uncheck the box that says `Automatically detect settings.` And then, in the Proxy Server section, click the checkbox to enable `Use a proxy server for your LAN...`
* Enter `localhost` in HTTP Proxy and enter `8080` for the Port. Click OK.

**For Internet Explorer:**
* Download Chrome or Firefox.
* Never use Internet Explorer again.


## Built With

* Python 3.6
* Socket

## BUGS

Caching works fine for HTTPS but can not render HTTP pages properly.

## Contributing

1. Fork it
2. Create your feature branch: git checkout -b my-new-feature
3. Commit your changes: git commit -am 'Add some feature'
4. Push to the branch: git push origin my-new-feature
5. Submit a pull request

## Authors

Muhammad Ali Zia

## License

This project is licensed under the MIT License.

