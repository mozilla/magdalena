/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

var gProductData = {
    Firefox: {
        name: "Firefox Desktop",
        full: "Firefox",
        abbr: "ff",
        graphname: "fx",
        channels: {
            nightly: {
                name: "Nightly",
                versions: { },
                adi: { low: 8e4, min: 5e4 }, // ADUs
                rateBrCo: { high: 2.0, max: 3.0 }, // browser+content crashes per 100 ADI
                browser: { high: 1.2, max: 1.5 }, // browser crashes per 100 ADI
                content: { high: 0.8, max: 1.5 }, // content crashes per 100 ADI
                startup: { high: 0.3, max: 0.6 }, // browser startup crashes per 100 ADI
                plugincrash: { high: .09, max: .2 }, // plugin crashes per 100 ADI
                pluginhang: { high: .05, max: .2 }, // plugin hangs per 100 ADI
            },
            aurora: {
                name: "Dev Ed",
                fullname: "Developer Edition",
                versions: { },
                adi: { low: 1.3e5, min: 1e5 },
                rateBrCo: { high: 1.5, max: 2.0 },
                browser: { high: 1.0, max: 1.2 },
                content: { high: 0.5, max: 0.8 },
                startup: { high: 0.25, max: 0.4 },
                plugincrash: { high: .09, max: .2 },
                pluginhang: { high: .05, max: .2 },
            },
            beta: {
                name: "Beta",
                versions: { },
                adi: { low: 2e6, min: 1.4e6 },
                rateBrCo: { high: 1.0, max: 1.25 },
                browser: { high: 1.0, max: 1.25 },
                content: { high: 0.01, max: 0.01 },
                startup: { high: 0.2, max: 0.25 },
                plugincrash: { high: .09, max: .2 },
                pluginhang: { high: .09, max: .2 },
            },
            release: {
                name: "Release",
                graphname: "rel",
                versions: { },
                adi: { low: 1e8, min: 7e7 },
                rateBrCo: { factor: 1, high: 0.95, max: 1.1 },
                browser: { high: 0.95, max: 1.1 },
                content: { high: 0.01, max: 0.01 },
                startup: { high: 0.15, max: 0.20 },
                plugincrash: { high: .09, max: .15 },
                pluginhang: { high: .09, max: .15 },
            },
        },
    },
    FennecAndroid: {
        name: "Firefox for Android",
        full: "FennecAndroid",
        abbr: "fna",
        graphname: "and",
        noplugin: true,
        nocontent: true,
        channels: {
            nightly: {
                name: "Nightly",
                versions: { },
                adi: { low: 1.5e3, min: 1e3 },
                rateBrCo: { high: 5, max: 9 },
                startup: { high: 2, max: 5 },
            },
            aurora: {
                name: "Aurora",
                versions: { },
                adi: { low: 1.5e3, min: 1e3 },
                rateBrCo: { high: 4, max: 7 },
                startup: { high: 1.5, max: 3 },
            },
            beta: {
                name: "Beta",
                versions: { },
                adi: { low: 9e4, min: 8e4 },
                rateBrCo: { high: 2.0, max: 2.5 },
                startup: { high: 0.75, max: 1 },
            },
            release: {
                name: "Release",
                graphname: "rel",
                versions: { },
                adi: { low: 4.4e6, min: 3.8e6 },
                rateBrCo: { high: 1.3, max: 1.6 },
                startup: { high: 0.35, max: 0.45 },
            },
        },
    },
};

window.onload = function() {
    make_table(data);
    $("#date").on("change", function() {
        var d = $(this).val();
        if (d) {
            window.location = "./dashboard?date=" + d;
        }
        return false;
    });
}

function get_num_style(product, channel, field, x) {
    var data = gProductData[product].channels[channel][field];
    if (field === "adi") {
        return x < data.min ? "faroff" : (x < data.low ? "outside" : "normal");
    } else {
        return x > data.max ? "faroff" : (x > data.high ? "outside" : "normal");
    }
}

function format_adi(n) {
    var e = Math.floor(Math.log10(n)),
        r = e % 3,
        b = e - r;
    if (b >= 3) {
        var units = ['k', 'M', 'G'],
            prec = r == 0 ? 1 : 0,
            u = units[Math.trunc(b / 3)  - 1],
            val = (n / Math.pow(10, b)).toFixed(prec);
        return val + u;
    } else {
        return n.toString();
    }
}

function format_versions(versions) {
    if (versions.length == 1) {
        return versions[0];
    } else {
        var re = new RegExp("^([0-9]+)(?:\\.([0-9]+))*[ab]?([0-9]*)$"),
            v = versions.map(function(x) {
                return {version: x,
                        nums: re.exec(x)
                                .slice(1)
                                .filter(y => y.length != 0)
                                .map(n => parseInt(n))};
            })
                        .sort((a, b) => a.nums < b.nums ? -1 : 1)
                        .map(x => x.version);
        return v[0] + " - " + v[v.length - 1];
    }
}

function format_rate(r) {
    return r.toFixed(2);
}

function infoEvent(event, source) {
    var cell = event.target;
    if (cell.tagName === "A") {
        cell = cell.parentNode;
    }
    var infobox = $("#infobox"),
        id = cell.getAttribute("id").toString().split("_"),
        product = id[0],
        kind = id[1],
        channel_num = parseInt(id[2]),
        info = data[product],
        limits = $("#infobox .limits");
    if (event.type === "mouseover" || event.type === "touchstart") {
        infobox.css("left", (cell.offsetParent.offsetLeft + cell.offsetLeft - 1) + "px");
        infobox.css("top", (cell.offsetParent.offsetTop + cell.offsetTop + cell.offsetHeight - 1) + "px");
        var nums = gProductData[product].channels[info.channel[channel_num]];
        if (kind === "versions") {
            $("#verinfo").text(info.versions[channel_num]);
        } else if (kind === "adi") {
            $("#limit1").text(format_adi(nums.adi.low));
            $("#limit2").text(format_adi(nums.adi.min));
            limits.addClass("low");
        } else {
            $("#limit1").text(format_rate(nums[kind].high));
            $("#limit2").text(format_rate(nums[kind].max));
            limits.addClass("high");
        }
        $("#infobox ." + kind).removeClass("info").addClass("current");

        infobox.css("display", "block");
    } else {
        infobox.css("display", "none");
        $("#infobox ." + kind).removeClass("current").addClass("info");
        if (kind === "versions") {
            $("#verinfo").text("");
        } else if (kind === "adi") {
            limits.removeClass("low");
        } else {
            limits.removeClass("high");
        }
        $("#limit1").text("");
        $("#limit2").text("");
    }
}

function make_link(parent, text, field, product, channel) {
    if (field === "rateBrCo" || field === "startup") {
        var pre = (product === "Firefox") ? "fx" : "and",
            chan = (channel === "release") ? "rel" : channel,
            post = (field === "startup") ? "-bcat" : "",
            a = $("<a></a>");
        a.attr("href", "../longtermgraph/index.html?" + pre + chan + post)
         .attr("target", "_blank")
         .text(text);
        parent.append(a);
    } else {
        parent.text(text);
    }
}

function make_table_for(data, fields, product, headers) {
    var tr = $("<tr></tr>"),
        row = $("#" + product + " .headers"),
        info = data[product],
        i = 0,
        events = ["mouseover", "mouseout", "touchstart", "touchleave"];
    tr.addClass("versions");
    for (let version of info.versions) {
        var td = $("<td></td>");
        td.text(format_versions(version));
        tr.append(td);
        td.attr("id", product + "_versions_" + i);
        events.map(x => td.bind(x, infoEvent));
       ++i;
    }
    row.after(tr);
    row = tr;

    adis = info.adi;
    for (let field of fields) {
        tr = $("<tr></tr>");
        tr.append($("<th>" + headers[field] + "</th>"));
        row.after(tr);
        row = tr;
        for (var i = 0; i < adis.length; ++i) {
            var td = $("<td></td>"),
                n = 0;
            if (field === "adi") {
                n = adis[i];
                td.text(format_adi(n));
            } else {
                n = info[field][i] / adis[i] * 100.;
                make_link(td, format_rate(n), field, product, info.channel[i]);
            }
            td.addClass("num");
            td.addClass(get_num_style(product, info.channel[i], field, n));
            td.attr("id", product + "_" + field + "_" + i);
            events.map(x => td.bind(x, infoEvent));
            tr.append(td);
        }
    }
}

function make_table(data) {
    var fields_fx = ["adi", "rateBrCo", "browser", "startup", "content", "plugincrash", "pluginhang"],
        fields_fna = ["adi", "rateBrCo", "startup"],
        headers = {"adi": "ADI",
                   "rateBrCo": "Crash rate (b+c)",
                   "browser": "Browser crashes",
                   "content": "Content crashes",
                   "startup": "Startup crashes",
                   "plugincrash": "Plugin crashes",
                   "pluginhang": "Plugin hangs"};
    make_table_for(data, fields_fx, "Firefox", headers);
    make_table_for(data, fields_fna, "FennecAndroid", headers);
}
