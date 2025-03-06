import json
from typing import Dict

class EleDevice:

    DEVICE_B  = "Battery"
    DEVICE_S  = "Switch"
    DEVICE_R  = "Resistance"
    DEVICE_V  = "Voltmeter"
    DEVICE_A  = "Ammeter"
    DEVICE_SR = "Sliding Rheostats"

    def __init__(self, id: int, name: str, bp1: int, bp2: int, bp3=-1, is_open=False):
        self.id = id
        self.name = name
        self.bp1 = bp1
        self.bp2 = bp2
        if name == EleDevice.DEVICE_SR:
            self.bp3 = bp3
        if name == EleDevice.DEVICE_S:
            self.is_open = is_open

class EleBindPos:
    BP_P = "Pos"
    BP_N = "Neg"
    BP_SR_P = "SR_P"
    BP_SR_NL = "SR_NL"
    BP_SR_NR = "SR_NR"
    BP_VA_PLOW = "VA_LOW"
    BP_VA_PHIGH = "VA_HIGH"

    def __init__(self, id: int, name: str, parent: int):
        self.id = id
        self.name = name
        self.parent = parent

class EleLine:
    def __init__(self, id: int, from_bp: int, to_bp: int, from_device=-1, to_device=-1):
        self.id = id
        self.from_bp = from_bp
        self.to_bp = to_bp
        self.from_device = from_device
        self.to_device = to_device

class EleState:
    def __init__(self, components: Dict[str, EleDevice], bps: Dict[str, EleBindPos], lines: Dict[str, EleLine]):
        self.components = components
        self.bps = bps
        self.lines = lines

    def dump(self) -> str:
        return json.dumps(self, default=lambda obj: obj.__dict__)

if __name__ == "__main__":
    state = EleState({
        0: EleDevice(0, EleDevice.DEVICE_B, 0, 1),
        1: EleDevice(1, EleDevice.DEVICE_R, 2, 3),
    }, {
        0: EleBindPos(0, EleBindPos.BP_P, 0),
        1: EleBindPos(1, EleBindPos.BP_N, 0),
        2: EleBindPos(2, EleBindPos.BP_P, 1),
        3: EleBindPos(3, EleBindPos.BP_N, 1),
    }, {
        0: EleLine(0, 0, 2),
        1: EleLine(1, 3, 1)
    })

    print(state.dump())