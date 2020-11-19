import configparser
import json
import re
import sys


class SSHConfig:
    '''
    Stores SSH_config as a dict while differentiating between default
    values, actual options, Subsystem definition and Match blocks
    '''
    def __init__(self):
        self.config = {
            "Defaults": {},
            "Options": {},
            "Subsystems": [],
            "Matches": []
        }

    def parse(self, path='/etc/ssh/sshd_config'):
        '''
        Parses sshd_config and stores it in self.config.
        '''

        try:
            with open(path, 'r') as content:
                line = content.readline()
                while line:
                    # Ignore empty lines
                    if re.match('^\s*$', line):
                        line = content.readline()
                        continue

                    print(f"Handling '{line.rstrip()}'")
                    if re.match('^#\S+', line) is not None:
                        m = re.match('^(?:#)(\S+)\s+(.*)$', line)
                        default_option = m[1]
                        default_value = m[2]
                        self.config["Defaults"][default_option] = default_value
                        print(f"Found default '{default_value}' for '{default_option}'")
                    elif re.match('^Subsystem', line) is not None:
                        m = re.match('^(?:Subsystem\s+)(\S+)\s+(.*)$', line)
                        self.config["Subsystems"].append({
                            "Name": m[1],
                            "Command": m[2]
                        })
                        print(f"Found subsystem command '{m[2]}' for '{m[1]}'")
                    elif re.match('^Match', line) is not None:
                        match_content, seek = self.parse_match(line, content)
                        if match_content is not None and 'entries' in match_content.keys():
                            print(f"Found 'Match' block, type '{match_content['type']}', affecting '{match_content['targets']}'")
                            for entry in match_content['entries']:
                                print(f"\tFound value '{m[2]}' for '{m[1]}'")
                            self.config['Matches'].append(match_content)
                        else:
                            print(f"Found empty 'Match' block, type '{match_content['type']}', affecting '{match_content['targets']}'")
                        # Go up one line since the last "readline()" in parse_match goes 1 too far
                        content.seek(seek)
                    elif re.match('^[A-Z]', line) is not None:
                        m = re.match('^(\S+)\s*(.*)$', line)
                        option = m[1]
                        value  = m[2]
                        self.config["Options"][option] = value
                        print(f"Found option '{value}' for '{option}'")
                    line = content.readline()
        except IOError as e:
            print("Issue while accessing file" + str(e))
            quit()
        except OSError as e:
            print("Issue while running program" + str(e))


    def parse_match(self, line, content):
        '''
        Parse sshd_config 'Match' block to a dict.
        Match block format : cf. `man sshd_config`, basically, the block ends when the indent returns to the beginning of the line
        The following 'Match' block in the file :
        Match User user1,user2,user3
            X11Forwarding no
            IgnoreRhosts yes
        Should result in the following dict
        {
            "Type" : "User",
            "Targets": "user1,user2,user3",
            "Entries": [
                "X11Forwarding": "no",
                "IgnoreRhosts": "yes"
            ]
        }
        '''
        match_content = {}
        # Retrieve initial position in file, should change on each readline
        seek = content.tell()
        # TODO : your code here
        return seek, match_content

sshd_config = SSHConfig()
sshd_config.parse()
# Pretty print the resulting dict
print(f"Resulting dict : {json.dumps(sshd_config.config, indent=1)}")
