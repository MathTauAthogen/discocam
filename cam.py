#!/usr/bin/env python3
import subprocess
import os
import signal
from threading import Timer

allowed_filters = ["fireworks", "disco", "color", "rock", "rickroll", "frame", "rotate"]

filter_data = [
    {
    "name": "disco",
    "inputs": ["static/disco.png"],
    "params": [["period", "magnitude"], ["3","500"]],
    "filter": "[#####][v]scale2ref=w=oh*mdar:h=ih/5[disco][v];[v][disco]overlay=x=W*4/10:y=0[v];[v]hue=\'h=!!magnitude!!+!!magnitude!!*sin(2*PI*t/!!period!!)\'[v]"
    },
    {
    "name": "fireworks",
    "inputs": ["static/fireworks.png"],
    "params": [[],[]],
    "filter": "[#####][v]scale2ref=h=ow/mdar:w=iw*1/3[fireworks][v];[v][fireworks]overlay[v]",
    },
    {
    "name": "color",
    "inputs": [],
    "params": [["period", "magnitude"], ["3","500"]],
    "filter": "[v]hue=\'h=!!magnitude!!+!!magnitude!!*sin(2*PI*t/!!period!!)\'[v]",
    },
    {
    "name": "rock",
    "params": [["period", "magnitude"], ["3","0.005"]],
    "inputs": [],
    "filter": "[v]rotate=\'PI*!!magnitude!!*sin(2*PI*t/!!period!!)\'[v]",
    },
    {
    "name": "rickroll",
    "inputs": ["static/disco.png"],
    "params": [["period", "magnitude"], ["3","500"]],
    "filter": "[#####][v]scale2ref=w=oh*mdar:h=ih/5[disco][v];[v][disco]overlay=x=W*4/10:y=0[v];[v]hue=\'h=!!magnitude!!+!!magnitude!!*sin(2*PI*t/!!period!!)\'[v]"
    },
    {
    "name": "frame",
    "inputs": ["static/frame.mp4"],
    "params": [[],[]],
    "filter": "[#####][v]scale2ref=iw*1:-1[rickroll][v];[rickroll]colorkey=color=white:similarity=0.1[rickroll];[v][rickroll]overlay=x=0:y=0[v]"
    },
    {
    "name": "rotate",
    "inputs": [],
    "params": [["angle"], ["1"]],
    "filter": "[v]rotate=\'PI*!!angle!!\'[v]",
    },

]

filter_data = {x['name']: x for x in filter_data}

class Cam:
    def __init__(self):
        self.orig_inputs = ["/dev/video0"]
        self.orig_output = "v4l2 /dev/video2"
        self.orig_filters = ["[0]format=yuv420p[v]"]
        self.effects = []
        self.command = ""
        self.process = None

    def parse_input(self, words, allowed_keys, defaults):
        words = [i.lower() for i in words]
        parsed = []
        for i in range(len(allowed_keys)):
            try:
                ind = words.index(allowed_keys[i])
            except:
                ind = -1
            if(ind != -1):
                parsed += [[i, words[ind+1]]]
            else:
                parsed += [[i, defaults[i]]]
        return parsed

    def add_generic_effect(self, params, name):
        effect_data = filter_data[name]
        params = self.parse_input(params, effect_data["params"][0], effect_data["params"][1])
        filter_string = effect_data["filter"]
        for i in params:
            temp = filter_string.split("!!" + effect_data["params"][0][i[0]] + "!!")
            filter_string = str(i[1]).join(temp)
        self.effects.append({
            "name": effect_data["name"],
            "inputs": effect_data["inputs"],
            "filter": filter_string 
        })
    
    def add_rickroll(self, params):
        params = self.parse_input(params, ["position"], ["topright"])

        self.effects.append({
            "name": "rickroll",
            "inputs": ["static/rickroll.mp4"],
            #"filter": "[#####][v]scale2ref=w=oh*mdar:h=ih/4[rickroll][v];[v][rickroll]overlay=x=W*2/3:y=H/12[v]"
            "filter": "[#####][v]scale2ref=w=oh*mdar:h=ih/4[rickroll][v];[rickroll]fillborders=left=30:right=30:mode=smear[rickroll];[v][rickroll]overlay=x=W*2/3:y=H/12[v]"
            #"filter": "[#####][v]scale2ref=w=oh*mdar:h=ih/4[rickroll][v];[v][rickroll]overlay=x=W*2/3:y=H/12[v]"
        })

    def add_justify(self, params):
        self.effects.append({
            "name": "justify",
            "inputs": [],
            "filter": "[v]fillborders[v]",
        })

    def generate_cmd(self):
        self.inputs = self.orig_inputs[:]
        self.output = self.orig_output
        self.filters = self.orig_filters[:]

        ## Generate indexed filters
        next_input = len(self.inputs)
        for effect in self.effects:
            num_inputs = len(effect["inputs"])
            current_filter = effect["filter"]
            if num_inputs == 1:
                current_filter = current_filter.replace("#####", str(next_input))
                next_input += num_inputs # 1
            elif num_inputs > 1:
                pass # NOT IMPLEMENTED
            
            self.filters.append(current_filter)
            self.inputs += effect["inputs"]
        
        ## Generate command
        self.command = "ffmpeg "
        self.command += "-i " + " -i ".join(self.inputs) + " "
        if self.filters:
            self.command += "-filter_complex \""
            self.command += ";".join(self.filters)
            self.command += "\" "
        self.command += "-map \"[v]\" "
        self.command += "-f " + self.output
    
    def run_cmd(self):
        if self.process:
            #self.process.terminate()
            os.system("pkill ffmpeg")
        self.process=True
        subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        # os.system(self.command)
        # out,err=self.process.communicate()

        # print('output is: \n', out)
        # print('error is: \n', err)
    
    def shutdown(self):
        if self.process:
            os.system("pkill ffmpeg")
            #self.process.terminate()

    def restart_ffmpeg(self):
        if self.process:
            #self.process.terminate()
            os.system("pkill ffmpeg")
        self.process=subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        t = Timer(300, self.restart_ffmpeg, [])
        t.start()


    
this_filter = "[v]rotate=PI[v];"
another_filter = "[v][2]overlay=auto[v];"

if __name__ == "__main__":
    cam = Cam()
    t = Timer(300, cam.restart_ffmpeg, [])
    t.start()
    cam.generate_cmd()
    cam.run_cmd()
    while True:
        command = input("Enter a command > ")
        words = command.split(" ")
        if words[0] == "exit":
            cam.shutdown()
            break
        elif words[0] == "add":
            if(len(words) == 1):
                print("Needs a filter to add!")
                continue
            function = words[1].lower()
            if(function in allowed_filters):
                if(function != "rickroll"):
                    cam.add_generic_effect(words[2:], function)
                else:
                    cam.add_rickroll(words[2:])
            else:
                print("function not recognized")
        elif words[0] == "remove":
            if(len(words) == 1):
                    print("Needs an effect to remove!")
                    continue
            cam.effects = [i for i in cam.effects if i["name"] != words[1].lower()]
        elif words[0] == "list":
            for i in range(len(cam.effects)):
                print(str(i) + ". " + cam.effects[i]["name"])
        elif words[0] == "command":
            print(cam.command)
        elif words[0] == "swap":
            try:
                a = int(words[1])
                b = int(words[3])
            except:
                print("Please phrase your inquiry, \"Swap [first number] and [second number]\". Use the \"list\" command to get the numbers of each effect.")
                continue
            c = cam.effects[a]
            d = cam.effects[b]
            cam.effects[a] = d
            cam.effects[b] = c
        elif words[0] == "effects":
            print("Our current allowed effects are:")
            for i in range(len(allowed_filters)):
                print(str(i) + ". " + allowed_filters[i])
        elif words[0] == "help":
            print("Welcome to the Spicy Cam!")
            print("Use the \"effects\" command to see all allowed effects at this time.")
            print("Type \"help\" to see this help page.")
            print("Type \"swap [first number] and [second number]\" to swap the order application of two effects. use the \"list\" command to see all current effects.")
            print("Type \"command\" to see and copy the current ffmpeg command")
            print("Type \"add\" and then an effect name to add an effect. Enter parameters after in the form \"[parameter name] [value]\". Any other text will be ignored")
            print("Type \"remove\" and then an effect name to remove all effects of that type")
            print("Type \"exit\" or Ctrl-C to exit.")
            print("That's it! Happy Camming!")
        else:
            print("Invalid command")
            continue
        
        cam.generate_cmd()
        #print(cam.command)
        cam.run_cmd()

    cam.shutdown()
# add rotate speed 2
# remove rotate

# add rotate speed 2
# add rotate by angle PI

