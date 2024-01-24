/** @odoo-module **/

import {registry} from "@web/core/registry";
import {patch} from "@web/core/utils/patch";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {DocumentKanbanRenderer} from "./dms_document_kanban_renderer.esm";
import {DocumentKanbanController} from "./dms_document_kanban_controller.esm";

import {FileDropZone, FileUpload} from "./dms_document_upload.esm";

patch(DocumentKanbanRenderer.prototype, "document_kanban_renderer_zone", FileDropZone);
patch(DocumentKanbanController.prototype, "document_kanban_controller_upload", FileUpload);
DocumentKanbanRenderer.template = "dms.KanbanRenderer";

export const DocumentKanbanView = {
    ...kanbanView,
    buttonTemplate: "dms.KanbanButtons",
    Controller: DocumentKanbanController,
    Renderer: DocumentKanbanRenderer,
};

registry.category("views").add("document_kanban", DocumentKanbanView);
