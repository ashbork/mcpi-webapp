from flask import Flask
from flask import render_template
from mcpi.minecraft import Minecraft
from flask import request


class MinecraftSession:
    def __init__(self):
        self.mc = None
        self.x = 0
        self.y = 0
        self.z = 0
        self.facing = "N"
        self.visible = False
        self.showas = "REDSTONE_BLOCK"
        self.prev_block = self.curr_block
        self.attempt_connection()

    def attempt_connection(self):
        try:
            self.mc = Minecraft.create()
        except ConnectionRefusedError:
            print("No connection to Minecraft server.")
            self.mc = None

    @property
    def coords_transformed(self):
        return self.x, self.y + 60, self.z

    def status(self):
        # return 'up' if connection is up, attempt connection and return 'down' if connection is down
        self.attempt_connection()
        if self.mc is None:
            return "down"
        else:
            return "up"

    def move(self, direction):

        if self.visible:
            self._undraw_self()
        if direction == "forward":
            if self.facing == "N":
                self.z -= 1
            elif self.facing == "E":
                self.x += 1
            elif self.facing == "S":
                self.z += 1
            elif self.facing == "W":
                self.x -= 1
        elif direction == "backward":
            if self.facing == "N":
                self.z += 1
            elif self.facing == "E":
                self.x -= 1
            elif self.facing == "S":
                self.z -= 1
            elif self.facing == "W":
                self.x += 1
        elif direction == "up":
            self.y += 1
        elif direction == "down":
            self.y -= 1
        if self.visible:
            self.prev_block = self.curr_block
            self._draw_self()
        return self.response()

    @property
    def curr_block(self):
        if self.mc is not None:
            return self.mc.getBlock(self.coords_transformed)

    def _draw_self(self):
        if self.mc is not None:
            self.mc.setBlock(self.coords_transformed, self.showas)

    def _undraw_self(self):
        if self.mc is not None:
            self.mc.setBlock(self.coords_transformed, self.prev_block)

    def response(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "facing": self.facing,
            "block": self.curr_block,
        }

    def turn(self, direction):
        if direction == "left":
            if self.facing == "N":
                self.facing = "W"
            elif self.facing == "E":
                self.facing = "N"
            elif self.facing == "S":
                self.facing = "E"
            elif self.facing == "W":
                self.facing = "S"
        elif direction == "right":
            if self.facing == "N":
                self.facing = "E"
            elif self.facing == "E":
                self.facing = "S"
            elif self.facing == "S":
                self.facing = "W"
            elif self.facing == "W":
                self.facing = "N"
        return {"facing": self.facing}

    def teleport(self, x, y, z):
        self._undraw_self()
        self.x = x
        self.y = y
        self.z = z
        if self.visible:
            self._draw_self()
        return self.response()


app = Flask(__name__)
session = MinecraftSession()


@app.route("/")
def main_site():
    return render_template("index.html")


@app.route("/status", methods=["GET"])
def get_status():
    status = session.status()
    return {"status": status}


@app.route("/cursor", methods=["GET"])
def get_player_state():
    return {
        "x": session.x,
        "y": session.y,
        "z": session.z,
        "facing": session.facing,
        "block": session.curr_block,
    }


@app.route("/move", methods=["POST"])
def move():
    direction = request.form["direction"]
    return session.move(direction)


@app.route("/turn", methods=["POST"])
def turn():
    direction = request.form["direction"]
    return session.turn(direction)


@app.route("/teleport", methods=["POST"])
def teleport():
    x = int(request.form["x"])
    y = int(request.form["y"])
    z = int(request.form["z"])
    return session.teleport(x, y, z)


@app.route("/toggle_visibility", methods=["POST"])
def toggle_visibility():
    vis = request.form["visibility"]
    if vis == "show":
        session.visible = True
    elif vis == "hide":
        session.visible = False
    return {}
