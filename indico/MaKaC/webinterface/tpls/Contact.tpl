<div class="container" style="max-width: 700px;">
    <div class="groupTitle">${ _("Indico contact information")}</div>


    <div class="indicoHelp">
        % if supportEmail.strip():
        <div class="title">${ _("Getting help")}</div>

        <div class="content">
            <p><em>${ _("For support using ILC Agenda please contact the support line:")}</em></p>

            <div style="margin: 15px 50px;"><a href="mailto:${ supportEmail }">${ supportEmail }</a></div>
        </div>
        % endif
    </div>

</div>
