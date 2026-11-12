# Ghi chú phân tích · Day 04

Họ và tên: Giáp Mạnh Tuyên  
MSSV: 2A202603648

## 1. Case được chọn

- ID: H2.
- Yêu cầu: kiểm tra trạng thái GitHub Actions tại snapshot và xác minh một incident cụ thể, không khẳng định outage khi thiếu bằng chứng.
- Trong cả hai báo cáo hiện tại, H2 đạt 100/100. Hai kết quả này đều đã có bước kiểm tra trạng thái bổ sung nên không phản ánh kết quả H2 trước khi cải tiến.

## 2. Bằng chứng trong trace

Trace H2 trong cả `eval_before.json` và `eval_after.json` lần lượt ghi nhận `get_incident_details`, `validation_missing_status` và `get_status`. Agent đã đọc incident, được nhắc kiểm tra trạng thái dịch vụ rồi gọi tool kiểm tra trạng thái trước khi kết luận.

## 3. Cải tiến trong agent

Trong `agent.py`, khi câu hỏi cần trạng thái tại snapshot và agent đã tra incident nhưng chưa gọi status cho provider tương ứng, agent ghi `validation_missing_status` và yêu cầu model kiểm tra status trước khi kết luận. Nếu tool lỗi, model được yêu cầu nêu giới hạn thay vì đoán. Cải tiến này đã có mặt trong trace của cả hai file eval hiện tại.

## 4. So sánh hai báo cáo hiện có

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---:|---:|
| Điểm tổng | 99,32/100 | 100/100 |
| Số case được chấm | 22/22 | 22/22 |
| Điểm H2 | 100/100 | 100/100 |
| Model calls H2 | 5 | 5 |
| Token agent H2 | 9.854 | 10.082 |
| Token judge H2 | 1.895 | 1.914 |
| Model calls agent, toàn bộ case | 54 | 55 |
| Token agent, toàn bộ case | 93.352 | 93.484 |
| Token judge, toàn bộ case | 37.174 | 35.554 |
| Chi phí | Không có trong báo cáo | Không có trong báo cáo |

Hai file cùng cấu hình agent và judge `gemini-3.5-flash-lite`, temperature 0, dataset core và max steps 8. Điểm E1 thay đổi từ 95 lên 100; judge ở lần before nhận xét cần chú ý ngày tháng incident. Điểm A7 thay đổi từ 90 lên 100; judge ở lần before nhận xét có thể bổ sung các bước kiểm tra. Các nhận xét này là đánh giá của judge, cần đối chiếu trace.

Cả hai báo cáo được gộp từ các lượt chạy lại do một số case ban đầu chưa chấm được; metadata trong từng file ghi nguồn và cách xử lý. Một số case chỉ chạy lại judge và giữ nguyên kết quả agent. Tổng token ở bảng chỉ tính kết quả cuối được chọn cho từng case, không bao gồm các lượt thất bại hoặc chạy lại không được chọn.

## 5. Giới hạn

- Cả `eval_before.json` và `eval_after.json` đều đã có cải tiến H2. Chênh lệch điểm giữa chúng không chứng minh tác động trước–sau của cải tiến này. Cần một báo cáo trước cải tiến hợp lệ để thực hiện phép so sánh đó.
- File before không lưu mã phiên bản agent cho mọi lượt. File after ghi SHA-256 khớp với `agent.py` hiện tại. Việc gộp nhiều lượt và số lần chạy hạn chế chưa chứng minh độ ổn định.
- Điểm judge là ước lượng và cần đối chiếu trace. Snapshot chỉ phản ánh thời điểm thu thập, không xác nhận trạng thái thực tế hiện tại.

## Bonus

- `eval_bonus.json` có 10/10 case được chấm, dùng `gpt-5-nano` cho agent và judge, đạt 87,9/100, tương đương 13,19/15 điểm tham khảo.
- B2 đạt 50: trace có một lần đọc chi tiết incident, chưa đọc trang tiếp theo, nên thiếu cập nhật về upstream GitHub.
- B4 đạt 88: Vercel bị rate limit và agent dừng sau ba lần, báo không xác nhận được trạng thái; GitHub có kết quả.
- B9 đạt 80: agent không bịa trạng thái Linear/Slack nhưng vẫn gọi các provider không liên quan.
- Kết quả B2 và B9 cho thấy việc đọc đủ timeline khi cần và tránh gọi tool không liên quan vẫn cần cải thiện.
