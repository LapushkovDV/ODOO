/** @odoo-module **/

import {KanbanController} from "@web/views/kanban/kanban_controller";

export class DocumentKanbanController extends KanbanController {
    setup() {
        super.setup();
    }

    createDirectory() {
        const ctx = this.props.context;
        if (this.props.domain.length === 1) {
            ctx.default_parent_id = this.props.domain[0][2];
        } else {
            ctx.default_parent_id = this.props.domain[2][2];
        }

        this.orm.call(
            "ir.ui.view",
            "search_read",
            [[["name", "=", "dms.directory.form.quick_create"]]],
            { limit: 1 }
        ).then(formViewId => {
            this.actionService.doAction({
                name: this.env._t("Directory"),
                type: "ir.actions.act_window",
                res_model: "dms.directory",
                views: [[formViewId[0]["id"], 'form']],
                view_mode: "form",
                context: ctx,
                target: "new"
            });
        });
    }
}
