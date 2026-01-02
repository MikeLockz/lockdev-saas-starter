"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateFile = exports.generate = void 0;
const tslib_1 = require("tslib");
const promises_1 = tslib_1.__importDefault(require("fs/promises"));
const ts = tslib_1.__importStar(require("typescript"));
function getDefaultBanner() {
    return `/* eslint-disable */
// Generated using Tanu.js (https://github.com/ariesclark/tanu.js)
// Content generated is licensed under the MIT License.
`;
}
/**
 * Generate the file source as a string.
 * @param nodes An array of nodes.
 */
function generate(nodes, options = {}) {
    var _a;
    return tslib_1.__awaiter(this, void 0, void 0, function* () {
        (_a = options.banner) !== null && _a !== void 0 ? _a : (options.banner = getDefaultBanner());
        const file = ts.createSourceFile("", "", ts.ScriptTarget.ESNext, true);
        const printer = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed });
        return new Promise((resolve, reject) => {
            try {
                setImmediate(() => {
                    const printedNodes = printer.printList(ts.ListFormat.MultiLine, ts.factory.createNodeArray(nodes), file);
                    resolve(`${options.banner}\n${printedNodes}`);
                });
            }
            catch (error) {
                reject(error);
            }
        });
    });
}
exports.generate = generate;
function generateFile(path, nodes, options = {}) {
    return tslib_1.__awaiter(this, void 0, void 0, function* () {
        const source = yield generate(nodes, options);
        yield promises_1.default.writeFile(path, source, "utf-8");
    });
}
exports.generateFile = generateFile;
