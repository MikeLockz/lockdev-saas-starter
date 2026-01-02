"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tuple = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
const utils_1 = require("../utils");
function tuple(definitions) {
    return ts.factory.createTupleTypeNode(Array.isArray(definitions)
        ? definitions.map(utils_1.toTypeNode)
        : Object.entries(definitions).map(([key, value]) => {
            return ts.factory.createNamedTupleMember(undefined, ts.factory.createIdentifier(key), undefined, (0, utils_1.toTypeNode)(value));
        }));
}
exports.tuple = tuple;
