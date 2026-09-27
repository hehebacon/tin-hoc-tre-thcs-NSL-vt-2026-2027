#include "RobotAI.h"
void RobotAI::begin(){}
bool RobotAI::has(const String& t,const char* n){return t.indexOf(n)>=0;}
RobotAIResult RobotAI::think(const String& raw) const{
 String t=raw; t.trim(); t.toLowerCase();
 if(!t.length()) return {RobotAIIntent::NONE,"Hãy nói nhiệm vụ cho robot."};
 if(has(t,"dừng")||has(t,"dung")||has(t,"stop")||has(t,"khẩn cấp")) return {RobotAIIntent::STOP,"Đã nhận lệnh dừng an toàn."};
 if(has(t,"tiếp tục")||has(t,"tiep tuc")||has(t,"resume")) return {RobotAIIntent::RESUME,"Đã nhận lệnh tiếp tục."};
 if(has(t,"tự hành")||has(t,"tu hanh")||has(t,"tự động")||has(t,"tu dong")||has(t,"autonomous")) return {RobotAIIntent::AUTONOMOUS,"Chuyển sang nhiệm vụ tự hành."};
 if(has(t,"driver")||has(t,"điều khiển")||has(t,"dieu khien")) return {RobotAIIntent::DRIVER,"Chuyển sang Driver Control."};
 if(has(t,"end game")||has(t,"kết thúc")||has(t,"ket thuc")) return {RobotAIIntent::END_GAME,"Chuyển sang End Game."};
 if(has(t,"về nhà")||has(t,"ve nha")||has(t,"return")) return {RobotAIIntent::RETURN_HOME,"Đang chuẩn bị về vị trí xuất phát."};
 if(has(t,"cứu")||has(t,"rescue")) return {RobotAIIntent::RESCUE,"Đã nhận nhiệm vụ cứu hộ."};
 if(has(t,"tuần tra")||has(t,"tuan tra")||has(t,"patrol")) return {RobotAIIntent::PATROL,"Đã nhận nhiệm vụ tuần tra."};
 if(has(t,"đứng")||has(t,"stand")) return {RobotAIIntent::STAND,"Robot chuyển về tư thế đứng."};
 if(has(t,"center")||has(t,"trung tâm")) return {RobotAIIntent::CENTER,"Đưa robot về vị trí trung tâm."};
 if(has(t,"demo")) return {RobotAIIntent::DEMO,"Chạy chế độ trình diễn."};
 if(has(t,"trạng thái")||has(t,"trang thai")||has(t,"status")) return {RobotAIIntent::STATUS,"Đây là trạng thái hiện tại."};
 return {RobotAIIntent::NONE,"Tôi hiểu: tự hành, driver, end game, dừng, tiếp tục, về nhà, cứu hộ, tuần tra, đứng, center, demo, status."};
}
String RobotAI::name() const{return "XZORT Offline Robot AI";}