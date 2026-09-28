from dataclasses import asdict, dataclass
from math import sin, pi

@dataclass
class LegTarget:
    x: float
    y: float
    z: float
    phase: str

class GaitPlanner:
    """Alternating-diagonal gait with bounded stable/fast presets and smooth ramps."""
    LEGS=("FL","FR","RL","RR")
    LEG_PHASES={"FL":0.0,"RR":0.0,"FR":0.5,"RL":0.5}
    PRESETS={
        "STABLE_WALK":(24.0,20.0,1.15),
        "WALK":(34.0,22.0,1.65),
        "CRUISE":(34.0,22.0,1.65),
        "FAST":(44.0,24.0,2.05),
        "SLOW_WALK":(20.0,16.0,1.0),
        "SEARCH":(18.0,14.0,0.8),
        "RESCUE":(14.0,12.0,0.7),
    }
    def __init__(self):
        self.phase=0.0
        self.step_length=self.target_step_length=24.0
        self.step_height=self.target_step_height=20.0
        self.frequency=self.target_frequency=1.15
        self.body_height=-90.0
        self.foot_y={"FL":45.0,"RL":45.0,"FR":-45.0,"RR":-45.0}
        self.speed=self.target_speed=0.0
        self.moving=False
        self.move_name="IDLE"
    def set_moveset(self,name):
        name=str(name).upper()
        if name=="STABLE": name="STABLE_WALK"
        if name=="FAST_WALK": name="FAST"
        if name not in self.PRESETS and name!="IDLE": return False
        if name=="IDLE":
            self.target_speed=0.0; self.moving=False; self.move_name="IDLE"; return True
        self.move_name=name
        self.target_step_length,self.target_step_height,self.target_frequency=self.PRESETS[name]
        self.target_speed=1.0; self.moving=True
        return True
    def reset(self): self.__init__()
    def _leg_target(self,leg):
        y=self.foot_y[leg]
        if self.speed<=1e-3: return LegTarget(0.0,y,self.body_height,"STANCE")
        local=(self.phase-self.LEG_PHASES[leg])%1.0
        length=self.step_length*self.speed
        height=self.step_height*self.speed
        if local<0.5:
            p=local/0.5; x=-length/2.0+p*length; z=self.body_height+height*sin(p*pi); phase="SWING"
        else:
            p=(local-0.5)/0.5; x=length/2.0-p*length; z=self.body_height; phase="STANCE"
        return LegTarget(round(x,3),y,round(z,3),phase)
    def update(self,dt=0.05,moving=None):
        dt=max(0.001,min(0.1,float(dt)))
        if moving is not None:
            self.moving=bool(moving); self.target_speed=1.0 if self.moving else 0.0
        blend=min(1.0,dt*4.0)
        self.step_length+=(self.target_step_length-self.step_length)*blend
        self.step_height+=(self.target_step_height-self.step_height)*blend
        self.frequency+=(self.target_frequency-self.frequency)*blend
        ramp=2.5*dt
        if self.speed<self.target_speed:self.speed=min(self.target_speed,self.speed+ramp)
        else:self.speed=max(self.target_speed,self.speed-ramp)
        if self.speed>1e-3:self.phase=(self.phase+dt*self.frequency*self.speed)%1.0
        return {leg:self._leg_target(leg) for leg in self.LEGS}
    def snapshot(self,dt=0.05,moving=None):
        return {leg:asdict(target) for leg,target in self.update(dt,moving).items()}
    def telemetry(self):
        return {"mode":self.move_name,"speed_scale":round(self.speed,3),
                "step_length_mm":round(self.step_length,2),
                "step_height_mm":round(self.step_height,2),
                "frequency_hz":round(self.frequency,3)}


class JumpPlanner:
    """Simulator-safe jump sequence using coordinated 3-DOF leg compression/extension.

    This is a trajectory generator, not a claim that the physical robot can jump.
    Physical jump must be validated for servo torque, structure, landing and safety.
    """
    PHASES=("CROUCH","LOAD","PUSH","FLIGHT","TUCK","LAND","ABSORB","RECOVER")

    def __init__(self):
        self.phase_index=0
        self.t=0.0
        self.active=False
        self.done=False
        self.duration={"CROUCH":0.22,"LOAD":0.16,"PUSH":0.14,"FLIGHT":0.28,
                       "TUCK":0.12,"LAND":0.12,"ABSORB":0.18,"RECOVER":0.22}

    @property
    def phase(self):
        return self.PHASES[self.phase_index]

    def start(self):
        self.phase_index=0
        self.t=0.0
        self.active=True
        self.done=False

    def stop(self):
        self.active=False
        self.done=False

    def update(self,dt=0.02):
        if not self.active:
            return {"active":False,"phase":"IDLE","progress":0.0}
        dt=max(0.001,min(0.05,float(dt)))
        self.t+=dt
        while self.t>=self.duration[self.phase]:
            self.t-=self.duration[self.phase]
            if self.phase_index>=len(self.PHASES)-1:
                self.active=False
                self.done=True
                return {"active":False,"phase":"DONE","progress":1.0}
            self.phase_index+=1
        total=self.duration[self.phase]
        p=max(0.0,min(1.0,self.t/total))
        return {"active":True,"phase":self.phase,"progress":p}

    def leg_pose(self,leg):
        # x/y remain planted relative to the body; z changes through
        # coordinated compression -> extension -> flight -> absorption.
        y={"FL":45.0,"RL":45.0,"FR":-45.0,"RR":-45.0}[leg]
        z0=-90.0
        if self.phase=="CROUCH":
            p=self.t/self.duration["CROUCH"]; z=z0-22.0*p
        elif self.phase=="LOAD":
            p=self.t/self.duration["LOAD"]; z=-112.0
        elif self.phase=="PUSH":
            p=self.t/self.duration["PUSH"]; z=-112.0+42.0*p
        elif self.phase in ("FLIGHT","TUCK"):
            z=-70.0
        elif self.phase=="LAND":
            p=self.t/self.duration["LAND"]; z=-70.0-20.0*p
        elif self.phase=="ABSORB":
            p=self.t/self.duration["ABSORB"]; z=-90.0-10.0*sin(p*pi)
        else:
            p=self.t/self.duration["RECOVER"]; z=-100.0+10.0*p
        return LegTarget(0.0,y,z,self.phase)
