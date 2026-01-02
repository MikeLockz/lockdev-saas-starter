"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.type = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../../utils");
const utils_2 = require("../utils");
const constructType = (name, definition) => {
    return ts.factory.createTypeAliasDeclaration(undefined, [ts.factory.createModifier(ts.SyntaxKind.ExportKeyword)], name, undefined, (0, utils_2.toTypeNode)(definition));
};
/**
 * Create an explicit type.
 *
 * @param name The type name.
 * @param definition The type definition.
 */
function type(name, definition) {
    if (typeof definition !== "function")
        return constructType(name, definition);
    return (0, utils_1.setLazy)(constructType(name, {}), () => constructType(name, definition()));
}
exports.type = type;
