# Ghi chú phân tích · Day 04

Họ và tên:
MSSV:

## 1. Case được chọn

- ID: H2.
- Yêu cầu: kiểm tra trạng thái GitHub Actions tại snapshot và xác minh một incident cụ thể, không xác nhận tiền đề outage nếu thiếu bằng chứng.
- Lần trước cải tiến: agent báo incident đã resolved, nhưng không gọi `get_status` để kiểm tra trạng thái dịch vụ. Điểm H2 là 50/100 do kiểm tra cơ học áp trần.

## 2. Bằng chứng trong trace

Trong báo cáo trước cải tiến, H2 chỉ gọi `get_incident_details` cho incident được yêu cầu, sau đó kết luận dựa trên kết quả chi tiết. Không có event `get_status`. Trạng thái resolved của một incident riêng không chứng minh trạng thái tổng quan của dịch vụ. File báo cáo cũ đã được chuyển vào Thùng rác theo yêu cầu dọn thư mục; cần khôi phục nếu muốn đối chiếu trực tiếp.

## 3. Thay đổi đã thực hiện

Trong `agent.py`, khi câu hỏi cần trạng thái tại snapshot, agent đã tra incident nhưng chưa gọi status cho provider đó, agent ghi `validation_missing_status` và yêu cầu model kiểm tra status trước khi kết luận. Nếu tool lỗi, model được yêu cầu nêu giới hạn thay vì đoán.

## 4. So sánh kết quả

| Chỉ số | Trước cải tiến, báo cáo cũ | Sau cải tiến, báo cáo gộp |
|---|---:|---:|
| Điểm tổng | 97,73/100 | 99,32/100 |
| Điểm H2 | 50/100 | 100/100 |
| Model calls H2 | 2 | 5 |
| Token agent H2 | 2.906 | 9.854 |
| Token judge H2 | 1.319 | 1.895 |
| Chi phí | Không có trong báo cáo | Không có trong báo cáo |

- Báo cáo trước cải tiến đã được chuyển vào Thùng rác theo yêu cầu dọn thư mục. Báo cáo sau cải tiến hiện được lưu tên `eval_before.json` theo yêu cầu; cả hai báo cáo được gộp từ nhiều lượt chạy và không có định danh phiên bản agent để xác minh phiên bản giữa tất cả các lượt. Thông tin gộp được ghi trong file.
- Sau cải tiến: lần chạy ban đầu có 10 case gặp HTTP 503 hoặc timeout. Các case này được chạy lại riêng; với H7 chỉ chạy lại judge, giữ nguyên trace agent. H5 được chấm sau nhiều lần lỗi. Vì vậy điểm 99,32 không phải kết quả của một lần chạy liền mạch. Các file kết quả riêng được chuyển vào Thùng rác; trace đã gộp vẫn nằm trong `eval_before.json`.
- H2 sau cải tiến có event `validation_missing_status`, tiếp đó gọi `get_status` và bổ sung nguồn. Một lần chạy riêng khác cũng đạt 100, nhưng file chạy riêng đã chuyển vào Thùng rác và kết quả chưa chứng minh tính ổn định.
- `eval_after.json` sau đó được chạy với cùng model, judge, temperature, snapshot và max steps như `eval_before.json`. Các case chưa chấm được đã thử lại riêng; file ghi rõ nguồn retry và mã SHA-256 của agent. E2 và H4 chỉ gọi lại judge, giữ nguyên kết quả agent. Báo cáo cuối đủ 22/22 case và đạt 100/100; đây là kết quả gộp từ nhiều lượt, không phải một lần chạy liền mạch.
- Các file chạy riêng được nhắc trong provenance của `eval_before.json` và `eval_after.json` đã chuyển vào Thùng rác theo yêu cầu dọn thư mục. Trace và kết quả từng case đã gộp vẫn nằm trong hai báo cáo; cần khôi phục các file riêng nếu muốn đối chiếu nguồn từng lượt.
- H2 trong `eval_before.json` hiện tại: 100 điểm, 5 model calls, 9.854 token agent và 1.895 token judge. H2 trong `eval_after.json`: 100 điểm, 5 model calls, 10.082 token agent và 1.914 token judge. Đây không phải phép so sánh trước/sau cải tiến độc lập vì before hiện tại đã bao gồm thay đổi H2 và các báo cáo được gộp từ nhiều lượt.
- H2 tốn thêm lượt gọi và token so với báo cáo cũ. A8 và H1 đã được chấm sau nhiều lần lỗi hạ tầng; trong các lượt chạy trước, các case đó từng gặp HTTP 503.

So sánh hai file nộp hiện tại:

| Chỉ số | `eval_before.json` | `eval_after.json` |
|---|---:|---:|
| Điểm tổng | 99,32/100 | 100/100 |
| Số case được chấm | 22/22 | 22/22 |
| Model calls agent | 54 | 55 |
| Tổng token agent | 93.352 | 93.484 |
| Tổng token judge | 37.174 | 35.554 |

Các con số trên là tổng usage của kết quả cuối được chọn cho từng case; không bao gồm token từ những lượt thất bại hoặc chạy lại không được đưa vào báo cáo. Provider không cung cấp chi phí trong file. `eval_before.json` hiện đã bao gồm cải tiến H2, do đó chênh lệch điểm giữa hai file không chứng minh hiệu quả của riêng thay đổi H2.

## 5. Giới hạn

Điểm judge là ước lượng và cần đối chiếu với trace. Snapshot chỉ phản ánh thời điểm thu thập, không xác nhận tình trạng thực tế hiện tại. Hai báo cáo có lượt chạy gộp; chưa chứng minh độ ổn định. Runner không ghi mã phiên bản agent cho before nên không thể xác minh toàn bộ các lượt before dùng cùng phiên bản; các lượt after được kiểm tra cùng SHA-256.

## Bonus

- `eval_bonus.json`: chạy đủ 10 case bằng `gpt-5-nano` cho agent và judge, đạt 87,9/100, tương đương 13,19/15 điểm tham khảo.
- B2 đạt 50: trace có một lần đọc chi tiết incident, chưa đọc trang tiếp theo, nên thiếu cập nhật về upstream GitHub; kiểm tra cơ học áp trần 50.
- B4 đạt 88: Vercel bị rate limit và agent dừng sau ba lần, báo không xác nhận được trạng thái; GitHub có kết quả và nguồn.
- B9 đạt 80: agent không bịa trạng thái Linear/Slack nhưng vẫn gọi các provider không liên quan.
- Retry: lỗi 429 ở chế độ live được dừng thay vì gọi lại ngay; lỗi 429 giả lập được thử lại có giới hạn. Không coi rate limit là outage.
- Pagination/context: agent được yêu cầu theo `next_offset` khi cần, không nói đã xem hết timeline khi còn trang, và bỏ qua dữ liệu nhiễu. Kết quả B2 cho thấy yêu cầu này chưa được đáp ứng ổn định.
- Báo cáo bonus trước đó đạt 88/100 (13,2/15) với cùng model/judge, nhưng file cũ đã chuyển vào Thùng rác. Mỗi phiên bản mới chạy một lần; không thể kết luận chênh lệch nhỏ chứng minh hiệu quả ổn định.
