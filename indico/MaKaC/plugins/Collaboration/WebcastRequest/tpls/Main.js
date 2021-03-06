{
    checkParams : function () {
        return {
        }
    },

    errorHandler: function(event, error) {
        if (error.operation == "create") {
            CSErrorPopup($T("Could not send email to responsible"),
                         [Html.span("", $T("There was a problem when sending the notification email to the Webcast responsible:"), Html.br(), error.inner)])
        }
        if (error.operation == "edit") {
            CSErrorPopup($T("Could not send email to responsible"),
                         [Html.span("", $T("There was a problem when sending the notification email to the Webcast responsible:"), Html.br(), error.inner)])
        }
        if (error.operation == "remove") {
            CSErrorPopup($T("Could not send email to responsible"),
                        [Html.span("", $T("There was a problem when sending the notification email to the Webcast responsible:"), Html.br(), error.inner)])
        }
    },

    customText : function(booking) {
        if (booking.acceptRejectStatus === false && trim(booking.rejectReason)) {
            return $T("Rejection reason: ") + trim(booking.rejectReason);
        }
    },

    clearForm : function () {
        var formNodes = IndicoUtil.findFormFields($E('WebcastRequestForm'));
        IndicoUtil.setFormValues(formNodes, {'otherComments':''})
        if (!isLecture) {
            $E('allTalksRB').dom.checked = true;
            IndicoUI.Effect.disappear($E('contributionsDiv'));
        }
    },

    onLoad : function() {

        WRUpdateContributionList();

        IndicoUtil.enableDisableForm($E("WRForm"), WRWebcastCapable);

        if (!isLecture) {
            if (singleBookings['WebcastRequest'] && singleBookings['WebcastRequest'].bookingParams.talks == 'choose') {
                IndicoUI.Effect.appear($E('contributionsDiv'));
            }
        }

        if(!singleBookings['WebcastRequest']) {
            callFunction('WebcastRequest', 'clearForm');
        }
    }
}
