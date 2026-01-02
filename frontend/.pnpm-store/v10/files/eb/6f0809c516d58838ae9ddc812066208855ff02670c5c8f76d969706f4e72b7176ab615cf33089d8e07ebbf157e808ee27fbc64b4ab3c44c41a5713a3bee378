"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.as = exports.propertyOf = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const type_1 = require("../type");
const utils_1 = require("../type/utils");
const utils_2 = require("./utils");
tslib_1.__exportStar(require("./statements"), exports);
function propertyOf(definition, key) {
    const node = (0, utils_2.toRuntimeNode)(definition);
    if (typeof key === "number")
        return ts.factory.createElementAccessExpression(node, key);
    return ts.factory.createPropertyAccessExpression(node, key);
}
exports.propertyOf = propertyOf;
// eslint-disable-next-line @typescript-eslint/ban-types
function as(definition, type) {
    return ts.factory.createAsExpression((0, utils_2.toRuntimeNode)(definition), type === "const" ? (0, type_1.reference)("const") : (0, utils_1.toTypeNode)(type));
}
exports.as = as;
