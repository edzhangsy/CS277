# the 277 project

We combine the code for three roles in one repository.

Use the `python main.py agg` to start the server.

For other servers, just use the `python main.py` to start

> remember to start the server in background so it don't be killed when you disconnet you ssh.

The aggregator will read the `config.json` file
Then it will call the other machines' `config` interface and send them their config.
The config for other clients are stored under the `others` dictionary.
The key is the IP address, The value is the config.
Send the config to the corresponding client.
After receiving the config, which is a json from the aggregator, the other servers will register the blueprint dynamically based on the `type` in the config.
Check the `config.json` file and add configs if needed.

The configs should be self-explained.


When you want to start another experiment, just edit the `config.json`, restart the aggregator.

## development

Because each kind of server have different kinds of interfaces, we separate them into different blueprints.
See the flask documentation for what is blueprint.
If you are developing the `client`, just edit the `client.py` and add interfacs.
The config that received from the server is stored in the `config` variable in `client.py` or `switch.py`

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

To be convinient, let's use the node14, "10.10.1.15" as the aggregator.

*Remember not to add unless files when you commit.*

*Remember to start the all the clients first, then start the aggregator*
## SEAL

seal library should be compiled first.

You can run the `seal.sh` to set it up.


