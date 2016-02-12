function nFormatter(num) {
    if (num >= 1000000) {
        return "+" + (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    }

    if (num >= 1000) {
        return "+" + (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    }

    return num;
}

function totalUsersProfiles() {
    $.getJSON("/dashboard/get-totals-users/", function() {
    }).done(function(info) {
        $("#users").html(nFormatter(info.total)).attr("title", info.total);
        $("#profiles").html(nFormatter(info.profiles)).attr("title", info.profiles);
        $("#usersNoProfile").html(nFormatter(info.users)).attr("title", info.users);
        $("#deletedUsers").html(nFormatter(info.deleted)).attr("title", info.deleted);
    });
}