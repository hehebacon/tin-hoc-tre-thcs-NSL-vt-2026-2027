#include "GaitController.h"
#include <math.h>

namespace {
constexpr float RAMP_RATE=2.5f;
constexpr float PARAM_RATE=4.0f;
constexpr float MIN_DT=0.001f;
constexpr float MAX_DT=0.10f;
}

GaitController::GaitController()
    : phaseValue(0), stepLengthValue(24), stepHeightValue(20), frequencyValue(1.15f),
      targetStepLength(24), targetStepHeight(20), targetFrequency(1.15f),
      bodyHeight(-90), speedValue(0), targetSpeed(0), active(false), modeName("IDLE") {}

void GaitController::reset() {
    phaseValue=0;
    stepLengthValue=targetStepLength=24;
    stepHeightValue=targetStepHeight=20;
    frequencyValue=targetFrequency=1.15f;
    speedValue=targetSpeed=0;
    active=false;
    modeName="IDLE";
}

void GaitController::configure(float stepLength,float stepHeight,float frequency) {
    targetStepLength=stepLength;
    targetStepHeight=stepHeight;
    targetFrequency=frequency;
    targetSpeed=1.0f;
    active=true;
}

void GaitController::setMode(const String& mode) {
    String m=mode; m.trim(); m.toUpperCase();
    if(m=="STABLE"||m=="STABLE_WALK"){configure(24,20,1.15f);modeName="STABLE_WALK";}
    else if(m=="WALK"||m=="CRUISE"){configure(34,22,1.65f);modeName=(m=="CRUISE"?"CRUISE":"WALK");}
    else if(m=="FAST"||m=="FAST_WALK"){configure(44,24,2.05f);modeName="FAST";}
    else if(m=="SLOW_WALK"){configure(20,16,1.0f);modeName="SLOW_WALK";}
    else if(m=="SEARCH"){configure(18,14,0.8f);modeName="SEARCH";}
    else if(m=="RESCUE"){configure(14,12,0.7f);modeName="RESCUE";}
    else reset();
}

void GaitController::stop(){targetSpeed=0;active=false;modeName="IDLE";}

void GaitController::update(float dt) {
    dt=fmaxf(MIN_DT,fminf(dt,MAX_DT));
    const float blend=fminf(1.0f,dt*PARAM_RATE);
    stepLengthValue+=(targetStepLength-stepLengthValue)*blend;
    stepHeightValue+=(targetStepHeight-stepHeightValue)*blend;
    frequencyValue+=(targetFrequency-frequencyValue)*blend;
    const float ramp=RAMP_RATE*dt;
    if(speedValue<targetSpeed) speedValue=fminf(targetSpeed,speedValue+ramp);
    else speedValue=fmaxf(targetSpeed,speedValue-ramp);
    if(speedValue<=0.001f){speedValue=0;return;}
    phaseValue+=dt*frequencyValue*speedValue;
    while(phaseValue>=1.0f) phaseValue-=1.0f;
}

float GaitController::legY(GaitLeg leg) const {
    return (leg==GAIT_FL||leg==GAIT_RL)?45.0f:-45.0f;
}
float GaitController::phaseOffset(GaitLeg leg) const {
    return (leg==GAIT_FL||leg==GAIT_RR)?0.0f:0.5f;
}
FootTarget GaitController::calculate(GaitLeg leg) const {
    FootTarget r={0,legY(leg),bodyHeight,false};
    if(speedValue<=0.001f)return r;
    float local=phaseValue-phaseOffset(leg);
    while(local<0) local+=1;
    while(local>=1) local-=1;
    const float length=stepLengthValue*speedValue;
    const float height=stepHeightValue*speedValue;
    if(local<0.5f){
        const float p=local/0.5f;
        r.x=-length*0.5f+p*length;
        r.z=bodyHeight+height*sinf(p*PI);
        r.swing=true;
    }else{
        const float p=(local-0.5f)/0.5f;
        r.x=length*0.5f-p*length;
    }
    return r;
}
FootTarget GaitController::target(GaitLeg leg) const{return calculate(leg);}
const char* GaitController::mode() const{return modeName.c_str();}
float GaitController::phase() const{return phaseValue;}
bool GaitController::moving() const{return speedValue>0.001f;}
float GaitController::speedScale() const{return speedValue;}
float GaitController::stepLength() const{return stepLengthValue;}
float GaitController::stepHeight() const{return stepHeightValue;}
float GaitController::frequency() const{return frequencyValue;}