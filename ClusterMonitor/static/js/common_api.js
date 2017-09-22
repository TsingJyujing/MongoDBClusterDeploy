/*
 * 一些公共的API存放的地方
 */


/*
 * 格式化byte大小
 */
function format_bytes(byte_count) {
    if (byte_count <= 1024.0) {
        return leave_point(byte_count, 100) + "b"
    } else {
        byte_count /= 1024.0;
        if (byte_count <= 1024.0) {
            return leave_point(byte_count, 100) + "kb"
        } else {
            byte_count /= 1024.0;
            if (byte_count <= 1024.0) {
                return leave_point(byte_count, 100) + "Mb";
            } else {
                byte_count /= 1024.0;
                if (byte_count <= 1024.0) {
                    return leave_point(byte_count, 100) + "Gb";
                } else {
                    return leave_point(byte_count / 1024.0, 100) + "Tb";
                }
            }
        }
    }
}

/*
 * 取小数点后N位
 */
function leave_point(num, ratio) {
    return Math.round(num * ratio) / ratio
}

/*
 * 将一个 List<Map<Any,Any>> 加载到表格中
 */
const load_table = (table_id, table_data) => {

    const table = $("#" + table_id);
    table.empty();
    //Container prepare
    const table_head = $("<tr></tr>");
    const table_body = $("<tbody></tbody>");
    table.append($("<thead></thead>").append(table_head));
    table.append(table_body);

    // static keys
    const keys = new Set();
    table_data.forEach((map_unit) => {
        for (let key in map_unit) keys.add(key);
    });
    const key_list = new Array();
    keys.forEach(val => key_list.push(val));

    key_list.forEach(
        val => {
            table_head.append(
                $("<th></th>").text(val).attr("align","center")
            )
        }
    );

    table_data.forEach(
        data => {
            const current_row = $("<tr></tr>");
            table_body.append(current_row);
            key_list.forEach(
                key => {
                    current_row.append(
                        $("<td></td>").text(
                            data[key] === undefined ? "-" : data[key]
                        ).attr("align","center")
                    )
                }
            )
        }
    )

};