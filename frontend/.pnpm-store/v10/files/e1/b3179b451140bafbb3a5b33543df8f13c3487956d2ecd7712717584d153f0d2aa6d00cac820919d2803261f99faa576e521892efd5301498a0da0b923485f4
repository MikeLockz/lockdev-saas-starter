"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.indexOf = exports.typeof = exports.array = exports.reference = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../runtime/utils");
const utils_2 = require("./utils");
tslib_1.__exportStar(require("./composites"), exports);
tslib_1.__exportStar(require("./declarations"), exports);
tslib_1.__exportStar(require("./modifiers"), exports);
tslib_1.__exportStar(require("./primitives"), exports);
function reference(node, typeArguments = []) {
    if (typeof node === "string")
        return ts.factory.createTypeReferenceNode(node, typeArguments.map(utils_2.toTypeNode));
    if (ts.isTypeNode(node))
        return node;
    return ts.factory.createTypeReferenceNode(node.name, typeArguments.map(utils_2.toTypeNode));
}
exports.reference = reference;
/**
 * Create an array type from a type definition.
 * @param definition The type definition.
 */
function array(definition) {
    return ts.factory.createTypeReferenceNode("Array", [(0, utils_2.toTypeNode)(definition)]);
}
exports.array = array;
function typeof_(value) {
    return ts.factory.createTypeQueryNode((0, utils_1.runtimeReference)(value));
}
exports.typeof = typeof_;
function indexOf(definition, index) {
    return ts.factory.createIndexedAccessTypeNode((0, utils_2.toTypeNode)(definition), (0, utils_2.typeLiteral)(index));
}
exports.indexOf = indexOf;
