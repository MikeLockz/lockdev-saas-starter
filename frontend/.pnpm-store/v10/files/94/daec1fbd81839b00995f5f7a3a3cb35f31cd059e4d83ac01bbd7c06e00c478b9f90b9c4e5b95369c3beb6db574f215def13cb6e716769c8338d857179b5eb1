"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.comment = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("./runtime/utils");
const utils_2 = require("./type/utils");
function comment(definition, value) {
    const node = (0, utils_2.isTypeDefinition)(definition) ? (0, utils_2.toTypeNode)(definition) : (0, utils_1.toRuntimeNode)(definition);
    const comment = Array.isArray(value) ? `*\n * ${value.join("\n * ")}\n ` : `* ${value} `;
    ts.addSyntheticLeadingComment(node, ts.SyntaxKind.MultiLineCommentTrivia, comment, true);
    return node;
}
exports.comment = comment;
