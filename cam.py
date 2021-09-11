#!/usr/bin/env python3
import subprocess
import os
import signal
from threading import Timer

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

    def add_justify(self, params):
        self.effects.append({
            "name": "justify",
            "inputs": [],
            "filter": "[v]fillborders[v]",
        })


    def add_colorcycle(self, params):
        params = self.parse_input(params, ["period", "magnitude"], ["3","2"])
        
        self.effects.append({
            "name": "color",
            "inputs": [],
            "filter": "[v]hue=\'h=" + params[1][1] + "+" + params[1][1] + "*sin(2*PI*t/" + params[0][1] + ")\'[v]",
        })
        
    def add_rock(self, params):
        params = self.parse_input(params, ["period", "magnitude"], ["3","0.005"])
        
        self.effects.append({
            "name": "rock",
            "inputs": [],
            "filter": "[v]rotate=\'PI*" + params[1][1] + "*sin(2*PI*t/" + params[0][1] + ")\'[v]",
        })

    def add_rickroll(self, params):
        params = self.parse_input(params, ["position"], ["topright"])

        self.effects.append({
            "name": "rickroll",
            "inputs": ["static/rickroll.mp4"],
            "filter": "[#####][v]scale2ref=iw*0.25:-1[rickroll][v];[rickroll]fillborders=left=23:right=23:mode=smear[rickroll];[v][rickroll]overlay=x=W*2/3:y=H/12[v]"
            #"filter": "[#####][v]scale2ref=iw*0.25:-1[rickroll][v];[v][rickroll]overlay=x=W*2/3:y=H/12[v]"
        })
    
    def add_frame(self, params):
        params = self.parse_input(params, ["position"], ["topright"])

        self.effects.append({
            "name": "frame",
            "inputs": ["static/frame.mp4"],
            "filter": "[#####][v]scale2ref=iw*1:-1[rickroll][v];[rickroll]colorkey=color=white:similarity=0.1[rickroll];[v][rickroll]overlay=x=0:y=0[v]"
        })


    def add_rotate(self, params):
        params = self.parse_input(params, ["angle"], ["1"])

        self.effects.append({
            "name": "rotate",
            "inputs": [],
            "filter": "[v]rotate=\'PI*" + params[0][1] + "\'[v]",
        })

    def add_rotate_2(self, params=None):
        if params != None:
            words = params.split(" ")
            if words[0].lower() == "speed":
                speed = words[1]

        self.effects.append({
            "name": "rotate",
            "inputs": [],
            "filter": "[v]rotate=" + angle + "[v]",
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
        self.process=subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
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
            function = words[1]
            if function == "rotate":
                cam.add_rotate(words[2:])
            elif function == "color":
                cam.add_colorcycle(words[2:])
            elif function == "rock":
                cam.add_rock(words[2:])
            elif function == "justify":
                cam.add_justify(words[2:])
            elif function == "rickroll":
                cam.add_rickroll(words[2:])
            elif function == "frame":
                cam.add_frame(words[2:])
            else:
                print("function not recognized")
        elif words[0] == "remove":
            if(len(words) == 1):
                    print("Needs a filter to remove!")
                    continue
            cam.effects = [i for i in cam.effects if i["name"] != words[1].lower()]
        elif words[0] == "list":
            for filter in cam.effects:
                print(filter["name"])
        elif words[0] == "command":
            print(cam.command)
        else:
            print("Invalid command")
            continue
        
        cam.generate_cmd()
        print(cam.command)
        cam.run_cmd()

    cam.shutdown()
# add rotate speed 2
# remove rotate

# add rotate speed 2
# add rotate by angle PI

