/** @odoo-module */

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";

import {DocumentKanbanRecord} from "./dms_document_kanban_record.esm";

export class DocumentKanbanRenderer extends KanbanRenderer {
    setup() {
        super.setup();
    }
}

DocumentKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: DocumentKanbanRecord,
};
