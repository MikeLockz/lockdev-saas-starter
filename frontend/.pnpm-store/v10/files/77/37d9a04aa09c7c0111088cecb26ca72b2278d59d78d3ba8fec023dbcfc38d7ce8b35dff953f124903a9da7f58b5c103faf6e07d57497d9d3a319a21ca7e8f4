"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setLazy = exports.isNode = exports.isPrimitive = exports.PrimitiveTypes = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
exports.PrimitiveTypes = ["string", "number", "boolean", "bigint" /*, "symbol" */];
function isPrimitive(value) {
    // @ts-expect-error: Readonly array include wants explicit value.
    return exports.PrimitiveTypes.includes(typeof value);
}
exports.isPrimitive = isPrimitive;
function isNode(value) {
    return (typeof value === "object" &&
        value !== null &&
        "kind" in value &&
        !!ts.SyntaxKind[value.kind]);
}
exports.isNode = isNode;
function setLazy(defaultValue, immediateValue) {
    let value = defaultValue;
    setImmediate(() => {
        value = immediateValue();
    });
    return new Proxy(defaultValue, {
        get(_, property, receiver) {
            return Reflect.get(value, property, receiver);
        }
    });
}
exports.setLazy = setLazy;
