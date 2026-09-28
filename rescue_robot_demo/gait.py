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
