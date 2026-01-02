"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.enum = void 0;
const tslib_1 = require("tslib");
const ts = tslib_1.__importStar(require("typescript"));
/**
 * Create an enum (uses the [enum type](https://www.typescriptlang.org/docs/handbook/enums.html) by default)
 *
 * @param name The name of the enum.
 * @param values An array of enum members.
 */
function enum_(name, values) {
    return ts.factory.createEnumDeclaration(undefined, [ts.factory.createModifier(ts.SyntaxKind.ExportKeyword)], name, values.map((value) => ts.factory.createEnumMember(value, undefined)));
}
exports.enum = enum_;
