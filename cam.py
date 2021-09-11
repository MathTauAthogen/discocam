import subprocess

class Cam:
    def __init__(self):
        self.orig_inputs = ["/dev/video0"]
        self.orig_output = "v4l2 /dev/video2"
        self.orig_filters = ["[0]format=yuv420p[v]"]
        self.effects = []
        self.command = ""
        self.process = None

    def parse_input(self, input, allowed_keys):
        input = input.lower()
        words = input.split(" ")
        parsed = []
        for i in len(allowed_keys):
            ind = words.index(allowed_keys[i])
            if(ind != -1):
                parsed += [[i, words[ind+1]]]
        return parsed

    def add_colorcycle(self, params):
        parse_input(params, ["period", "magnitude"])
        
        self.effects.append({
            "name": "cycle hue",
            "inputs": [],
            "filter": "[v]hue=\"h=" + + " \"[v]",
        })
    
    def add_rotate(self, angle="PI"):
        self.effects.append({
            "name": "rotate",
            "inputs": [],
            "filter": "[v]rotate=" + angle + "[v]",
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
        self.inputs = self.orig_inputs
        self.output = self.orig_output
        self.filters = self.orig_filters

        ## Generate indexed filters
        next_input = len(self.inputs)
        for effect in self.effects:
            num_inputs = len(effect["inputs"])
            current_filter = effect["filter"]
            if num_inputs == 1:
                current_filter = current_filter.replace("#####", next_input)
                next_input += num_inputs # 1
            elif num_inputs > 1:
                pass # NOT IMPLEMENTED
            
            self.filters.append(current_filter)
            self.inputs += effect["inputs"]
        
        ## Generate command
        self.command = "ffmpeg "
        self.command += "-i " + "-i ".join(self.inputs) + " "
        if self.filters:
            self.command += "-filter_complex \""
            self.command += ";".join(self.filters)
            self.command += "\" "
        self.command += "-map \"[v]\"] "
        self.command += "-f " + self.output
    
    def run_cmd(self):
        if self.process:
            self.process.terminate()
        self.process=subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        # out,err=self.process.communicate()

        # print('output is: \n', out)
        # print('error is: \n', err)
    
    def shutdown(self):
        if self.process:
            self.process.terminate()

    
this_filter = "[v]rotate=PI[v];"
another_filter = "[v][2]overlay=auto[v];"

if __name__ == "__main__":
    cam = Cam()
    while True:
        print()
        command = input("Enter a command > ")
        words = command.split(" ")
        if words[0] == "exit":
            cam.shutdown()
            break
        elif words[0] == "add":
            function = words[1]
            if function == "rotate":
                cam.add_rotate()
            else:
                print("function not recognized")
        elif words[0] == "remove":
            pass
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
