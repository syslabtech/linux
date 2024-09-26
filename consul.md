# Hashicorp Consul

Consul UI : http://127.0.0.1:8500/

> consul.hcl
```
datacenter = "consul-0"
data_dir = "/opt/consul"
client_addr = "0.0.0.0"
ui_config {
  enabled = true
}

server = true
bind_addr = "0.0.0.0"
advertise_addr = "127.0.0.1"
connect {
  enabled = true
}
#bootstrap_expect = 1
```

> Consul Service File Location ((/lib/systemd/system/consul.service)
```
[Unit]
Description="HashiCorp Consul - A service mesh solution"
Documentation=https://www.consul.io/
Requires=network-online.target
After=network-online.target
ConditionFileNotEmpty=/etc/consul.d/consul.hcl

[Service]
Type=notify
EnvironmentFile=-/etc/consul.d/consul.env
User=consul
Group=consul
ExecStart=/usr/bin/consul agent -config-dir=/etc/consul.d/
ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGTERM
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```
