# Setup a Jupyterhub on your RaspberryPi

This chapter is based on the [Setup-Guide](https://towardsdatascience.com/setup-your-home-jupyterhub-on-a-raspberry-pi-7ad32e20eed) by Gerold Busch.
The following steps must be followed in chronological order to ensure that the JupyterHub works properly:

1. Prepare Python Environment
2. Install JupyterHub
3. Configure JupyterHub as a system service

> Note
  ```
  It is recommended to change the default password and the default user name when setting up the RaspberryPi 
  for the first time. If there are several RaspberryPis in the network, the hostname should also be changed 
  to simplify a later connection via ssh. The hostname is important to address the Pi if the network assigns 
  dynamic IP addresses.
  ```


## Prepare Python environment

Redirect the system to python3:

```{r, eval=FALSE}
sudo rm /usr/bin/python 
sudo ln -s /usr/bin/python3 /usr/bin/python
```

Install the python package manager pip:

```{r, eval=FALSE}
sudo apt-get update 
sudo apt-get install python3-pip 
sudo pip3 install --upgrade pip
```

## Install JupyterHub

Install the proxy to routes the user requests to the hub and the notebook server:

```{r, eval=FALSE}
sudo apt-get install npm 
sudo npm install -g configurable-http-proxy
```

Install JupyterHub and Jupyter Notebook system-wide:

```{r, eval=FALSE}
sudo -H pip3 install notebook jupyterhub
```
or
```
sudo -H pip3 install --break-system-packages notebook jupyterhub
```
```{r, eval=FALSE}
pip3 install notebook jupyterhub
```

Create a JupyterHub configuration file:

```{r, eval=FALSE}
jupyterhub --generate-config 
sudo mv jupyterhub_config.py /root
```

In order to make changes at the Jupyterhub application, modify the `/root/jupyterhub_config.py`-File.
E.g. to change the port on which the JupyterHub runs, uncomment and modify the following line of the config file:

```{r, eval=FALSE}
c.JupyterHub.bind_url = 'http://:8888'
```

## Add virtual environment to JupyterHub
In order to add a virtual environment to the jupyter kernel list, first activate your environment. Afterwards run
```
pip install ipykernel
```
and then conclude the process by doing
```
sudo python -m ipykernel install --name "name_of_choice"
```

## Configure JupyterHub as a system service

To register JupyterHub as a system service, create the file `/lib/systemd/system/jupyterhub.service` and 
fill it with:

```{r, eval=FALSE}
[Unit] 
Description=JupyterHub Service 
After=multi-user.target  

[Service] 
User=root 
ExecStart=/usr/local/bin/jupyterhub --config=/root/jupyterhub_config.py 
Restart=on-failure 
 
[Install] 
WantedBy=multi-user.target
```

Make sure that the line starting with `ExecStart` contains the correct location of the JupyterHub binary and 
the config-file.

Afterwards, run the following commands:

```{r, eval=FALSE}
sudo systemctl daemon-reload 
sudo systemctl start jupyterhub 
sudo systemctl enable jupyterhub 
sudo systemctl status jupyterhub.service
```

Now the JupytherHub should be accessible under the link:

`http://<address of your raspi/hostname>:8888`

> Note
  ```
  This chapter did not include the data transfer to the RaspberryPi. It is recommended to 
  clone the repository on the RaspberryPi or to copy the local files between the computer and 
  the Pi via scp command or VNC.
  ```







