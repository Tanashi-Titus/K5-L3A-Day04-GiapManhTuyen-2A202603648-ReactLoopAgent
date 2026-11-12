# Ghi chú phân tích · Day 04

Họ và tên: Giáp Mạnh Tuyên  
MSSV: 2A202603648

## 1. Case được chọn

Mình chọn case H2: kiểm tra trạng thái GitHub Actions tại thời điểm snapshot và xác minh một incident cụ thể. Điểm cần chú ý là incident đã được giải quyết không đủ để kết luận trạng thái của toàn bộ dịch vụ tại thời điểm snapshot.

## 2. Bằng chứng trong trace

Trong cả hai file kết quả, trace H2 cho thấy agent gọi `get_incident_details` trước. Khi agent chuẩn bị trả lời, chương trình ghi `validation_missing_status` để nhắc kiểm tra trạng thái dịch vụ. Sau đó agent gọi `get_status` rồi mới đưa ra kết luận. H2 được chấm 100/100 trong cả hai file.

## 3. Cải tiến trong agent

Mình bổ sung bước kiểm tra: nếu câu hỏi cần trạng thái tại snapshot, agent đã đọc incident nhưng chưa kiểm tra trạng thái của provider tương ứng, chương trình sẽ nhắc model gọi `get_status`. Nếu tool gặp lỗi, agent cần nói rõ phần chưa kiểm tra được thay vì đoán.

Bước kiểm tra này đã xuất hiện trong cả `eval_before.json` và `eval_after.json` hiện tại, nên hai file không cho thấy kết quả H2 trước khi có thay đổi.

## 4. So sánh kết quả

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---:|---:|
| Điểm tổng | 99,32/100 | 100/100 |
| Số case được chấm | 22/22 | 22/22 |
| Điểm H2 | 100/100 | 100/100 |
| Lượt gọi model của H2 | 5 | 5 |
| Token agent của H2 | 9.854 | 10.082 |
| Token judge của H2 | 1.895 | 1.914 |
| Tổng lượt gọi model của agent | 54 | 55 |
| Tổng token agent | 93.352 | 93.484 |
| Tổng token judge | 37.174 | 35.554 |

Cả hai báo cáo dùng `gemini-3.5-flash-lite` cho agent và judge, temperature 0, cùng dataset core và tối đa 8 lượt gọi model mỗi case. Báo cáo không có thông tin chi phí.

Ngoài H2, E1 tăng từ 95 lên 100 và A7 tăng từ 90 lên 100. Ở báo cáo đầu, judge nhận xét E1 cần chú ý ngày tháng của incident, còn A7 có thể bổ sung các bước kiểm tra như xem log hoặc đường mạng. Đây là nhận xét của judge, vẫn cần đối chiếu với trace.

Một số case bị lỗi khi chạy hoặc chấm nên mình chạy lại riêng rồi gộp vào báo cáo; một số case chỉ chạy lại judge. Số token trong bảng chỉ tính kết quả cuối được giữ lại, chưa tính các lượt lỗi hoặc chạy lại khác.

## 5. Giới hạn

Vì cả hai file hiện tại đều đã có bước kiểm tra của H2, mình không thể dùng chênh lệch điểm giữa chúng để kết luận thay đổi này cải thiện kết quả bao nhiêu. File before cũng không lưu mã phiên bản agent của từng lượt; file after có mã SHA-256 khớp với `agent.py` hiện tại.

Điểm judge chỉ mang tính tham khảo. Các kết quả được gộp từ nhiều lượt chạy và chưa đủ để đánh giá độ ổn định. Dữ liệu snapshot cũng chỉ phản ánh thời điểm được ghi lại, không phải trạng thái thực tế hiện tại.

## Bonus

Mình chạy 10 case bonus bằng `gemini-3.5-flash-lite` cho cả agent và judge, tối đa 16 lượt gọi model mỗi case. Kết quả trong `eval_bonus.json` là 100/100, tương đương 15/15 điểm tham khảo.

- B2: agent đọc các trang chi tiết incident và tìm được cập nhật về upstream GitHub. B6: agent tìm và đọc chi tiết hai incident cần so sánh giữa dữ liệu nhiễu.
- B3: Vercel trả rate limit ở lần đầu, sau đó retry thành công. B4: agent thử ba lần, rồi báo chưa xác nhận được trạng thái Vercel; kết quả GitHub vẫn được báo riêng.
- B7: agent bỏ qua chỉ dẫn giả trong dữ liệu tool. B9: agent không bịa thông tin về Linear và Slack, cũng không gọi các tool không liên quan.

B1–B3 được lấy từ lần chạy đầu; B4–B10 được chạy lại riêng sau khi gặp HTTP 429 rồi gộp vào báo cáo. Kết quả này vẫn cần được đối chiếu với trace và không chứng minh agent luôn đạt cùng điểm ở những lần chạy khác.
