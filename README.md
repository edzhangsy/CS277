# the 277 project

We combine the code for three roles in one repository.

Use the `python main.py agg` to start the server.

For other servers, just use the `python main.py` to start

> remember to start the server in background so it don't be killed when you disconnet you ssh.

The aggregator will read the `config.json` file.
Then it will call the other machines' `config` interface and send them their config.
The config for other clients are stored under the `others` dictionary.
The key is the IP address, The value is the config.
Send the config to the corresponding client.
After receiving the config, which is a json from the aggregator, the other servers will register the blueprint dynamically based on the `type` in the config.
Check the `config.json` file and add configs if needed.

The configs should be self-explained.

When the type if client, there are `client_number` and `index`.
Which indicates how many clients is used in this experiment, and current client's index.
This is useful to divide the training and testing data set.
For example, a client is index 0 among 4 clients, so he will slice the data set into 4 slices, and he operates on the index 0 of the slices.


When you want to start another experiment, just edit the `config.json`, restart the aggregator.

## development

Because each kind of server have different kinds of interfaces, we separate them into different blueprints.
See the flask documentation for what is blueprint.
If you are developing the `client`, just edit the `client.py` and add interfaces.
The config that received from the server is stored in the `config` variable in `client.py` or `switch.py`
For example, if you are developing the client, the config that received from the server should be accessible in local `config` file.
If you want to send some data to the switch, just read the config, and get which address you should send to.
Then send to the interface of that address, for example, `http://10.10.1.5:5000/s/receive`.
Then, look at the status code!!
If it's 200, that is successful.
Look for the flask documentation for how to check the status code.
Also, you should write the log into the local `log` directory.
Just use some dictionary to store the logs.

For example, the log dictionary can be looked like this.

```
{
    "iteration": [
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        },
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        },
        {
            "start_time": "timestamp",
            "end_time": "timestamp",
            "byte_received": 50,
            "byte_send": 100
        }
    ]
}
```

I made this repo public
So, you can clone it anywhere you want.
I also add you guys the contributor on github.
When you want to make some changes, you develop somewhere, push it to github.
Then pull it in the cloudlab machines.

There are 15 machines on the cloudlab.
The 15 machines are connected physically using one switch.
And the address beginning with `10.10` is the local address.
The `node0` has address `10.10.1.1`.
The `node1` has address `10.10.1.2`
And so on.

For convenience, let's use the node14, `10.10.1.15` as the aggregator.

*Remember not to add unless files when you commit.*

*Remember to start the all the clients first, then start the aggregator*

*Maybe you should open the port 5000 using the iptables*

## SEAL

seal library should be compiled first.
After compilation, you can see the `seal.*.so`
Copy it under the directory of the this repo, and you should be able to use it by `import seal`

You can run the `seal.sh` to set it up.


## test

I have added the `test.py`.
The script will read part of the `config.json` and send out to the server, calling the config function.
