$(function () {

    var objScore = {};
    var len = $('textarea').length;
    $('input[type="radio"]').on('click', function () {
        var name = $(this).attr('name');
        var val = $(this).val();
        objScore[name] = val;
        // if (Object.getOwnPropertyNames(objScore).length === len) {
        //     $('#submit_svy').attr('disabled', false);
        // }
    });


    $('.submit_svy').on('click', function () {
        var commtens = '';
        $('textarea').each(function (i, o) {
            commtens += encodeURIComponent($(o).val()) + '|||'
        });

        if (commtens.length > 3) {
            commtens = commtens.substring(0, commtens.length - 3);
        }

        var arrScore = [];
        for (var prop in objScore) {
            if (objScore.hasOwnProperty(prop)) {
                arrScore.push(objScore[prop]);
            }
        }

        var status = arrScore.length == $('textarea').length ? '2' : '1'; //2 completed ,1 inprogressed
        var data = {
            score: arrScore.join('|||'),
            comments: commtens,
            status: status
        };
        var id = $('#svy_id').val();
        var nextsvyid = $(this).attr('nextsvyid');
        var prevurl = $(this).attr('previousurl');
        $.ajax({
            type: "POST",
            url: "/survey/completed/" + id,
            data: data,
            dataType: "json",
            success: function (data) {
                if (data['result'] === 'Success') {
                    if (!prevurl && !nextsvyid) {
                        alert("Thank you! Your survey has been submit successful!");
                        document.location.reload(true);
                    } else if (prevurl) {
                        document.location = prevurl;
                    } else {
                        document.location = '/survey/' + nextsvyid;
                    }
                } else {
                    alert("Error!");
                }
            }
        });
    });


    $('#submit_json_text').on('click', function () {
        $.ajax({
            type: "POST",
            url: "/upload_json",
            data: {
                json_text: $('#json_text').val()
            },
            dataType: "json",
            success: function (data) {
                if (data['result'] === 'Success') {
                    alert("Success!");
                    $('#json_text').val('')
                } else {
                    alert("Error!");
                    console.log(data);
                }
            }
        });
    });

    $('#submit_json_file').on('click', function () {
        var filePath = $('#File1').val();
        if(!filePath){
            alert('Please select a json file!');
            return;
        }

        $('form').submit();

    });

    $('.pager .next a').on('click', function () {
        var url = $(this).attr('url');
        if (url) {
            var arrScore = [];
            for (var prop in objScore) {
                if (objScore.hasOwnProperty(prop)) {
                    arrScore.push(objScore[prop]);
                }
            }
            if (arrScore.length && confirm('You have changed the data. Do you want save?')) {
                $('.btn-primary.submit_svy').click();
            } else {
                document.location = url;
            }
        }
    });
    $('.pager .previous a').on('click', function () {
        var url = $(this).attr('url');
        if (url) {
            var arrScore = [];
            for (var prop in objScore) {
                if (objScore.hasOwnProperty(prop)) {
                    arrScore.push(objScore[prop]);
                }
            }
            if (arrScore.length && confirm('You have changed the data. Do you want save?')) {
                $('.btn-default.submit_svy').attr('previousurl', url);
                $('.btn-default.submit_svy').click();
            } else {
                document.location = url;
            }
        }
    });

    $('.btn-delete').on('click', function () {
        var pkey = $(this).attr('pkey');
        if (!pkey) {
            return;
        }
        if (confirm('Do you want to delete this data set?')) {
            $.ajax({
                type: "POST",
                url: "/dataset/delete/" + pkey,
                dataType: "json",
                success: function (data) {
                    if (data['result'] === 'Success') {
                        document.location.reload(true);
                    } else {
                        alert("Error!");
                        console.log(data);
                    }
                }
            });
        }
    });


    var query = $('#Query');
    var w = query.width();
    var h = query.height();
    var wh = $(window).height();
    if (h >= wh) {
        h = wh - 10;
        query.css({
            height: h
        });
        $('.query-container').css({
            height: h - 100
        });
    }

    window.onscroll = function () {
        var topScroll = $(this.document).scrollTop();
        if (topScroll > 50) {
            query.css({
                top: '0',
                zIndex: '9999',
                position: 'fixed',
                width: w,
                height: h
            });
        } else {
            query.css({
                position: 'static'
            });
        }
    }

    var initSvyPage = function () {
        var arrCommtent = [];
        if (scoreStr) {
            arrScore = scoreStr.split('|||');
            arrScore.forEach(function (v, i) {
                var name = "svy_" + (i + 1);
                objScore[name] = v;
                $('input[type="radio"][name="' + name + '"][value="' + v + '"]').attr('checked', true);
            });
        }
        if (comments) {
            arrCommtent = comments.split('|||');
            $('textarea').each(function (i, o) {
                $(o).val(decodeURIComponent(arrCommtent[i]).replace(/&#39;/g, "'"));
            });
        }
    };



    var setNextPrevPage = function (svy_ids) {
        var curid = $('#svy_id').val();
        var previd = '';
        var nextid = '';
        if (svy_ids.length) {
            var index = svy_ids.findIndex(function (v, i) {
                return (v.id == curid);
            });

            if (index === svy_ids.length - 1) {
                //last
                nextid = '';
                $('.pager .next').addClass('disabled');

                previd = svy_ids[index - 1].id;
                if (previd) {
                    $('.pager .previous a').attr('url', "/survey/" + previd + "");
                } else {
                    $('.pager .previous').addClass('disabled');
                }
            } else if (index === 0) {
                //first
                previd = '';
                $('.pager .previous').addClass('disabled');

                nextid = svy_ids[index + 1].id;
                if (nextid) {
                    $('.pager .next a').attr('url', "/survey/" + nextid + "");
                } else {
                    $('.pager .next').addClass('disabled');
                }
            } else {
                nextid = svy_ids[index + 1].id;
                previd = svy_ids[index - 1].id;
                $('.pager .previous a').attr('url', "/survey/" + previd + "");
                $('.pager .next a').attr('url', "/survey/" + nextid + "");
            }

            if (nextid) {
                $('.btn-primary.submit_svy').attr('nextsvyid', nextid);
            } else {
                $('.btn-primary.submit_svy').attr('disabled', true);
            }

            //completed
            var completedQueries = 0;
            svy_ids.forEach(function (v, i) {
                if (v.status === 2) {
                    completedQueries++;
                }
            });

            var percentQueries = ((completedQueries / svy_ids.length) * 100).toFixed(0);
            $('.progress .progress-bar').css('width', percentQueries + '%');
            $('.progress .progress-bar span').text(percentQueries + '%');
        }
    };

    var getSurveyIds = function () {
        $.ajax({
            type: "GET",
            url: "/surveyids/" + $('#parent_pkey').val(),
            dataType: "json",
            success: function (data) {
                if (data['result'] === 'Success') {
                    setNextPrevPage(data['ids']);
                } else {
                    alert("Error!");
                    console.log(data);
                }
            }
        });
    };

    if (document.location.href.indexOf('survey/') != -1) {
        initSvyPage();
        getSurveyIds();
    }
});