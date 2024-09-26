Consul UI : http://<your-server-ip>:8500/

# consul.hcl
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
