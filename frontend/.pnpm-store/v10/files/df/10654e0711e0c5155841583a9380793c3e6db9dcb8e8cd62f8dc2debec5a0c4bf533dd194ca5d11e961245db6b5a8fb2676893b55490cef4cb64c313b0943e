import { AnyFunction, ObjectLiteral } from "../typings";
/** Returns a callback that will call all functions passed with the same arguments */
export declare const callAll: <Args = any, Fns extends Function = AnyFunction<Args, any>>(...fns: Fns[]) => (...args: Args[]) => void;
/** Returns a callback that will return true if all functions passed with the same arguments returns true */
export declare const needsAll: <Args = any, Fns extends Function = AnyFunction<Args, any>>(...fns: Fns[]) => (...args: Args[]) => boolean;
export type Composable<T = any, R = any> = (item: T) => R;
/** Compose left-to-right, most commonly used direction */
export declare const pipe: <T>(...fns: ((arg: T) => T)[]) => (value: T) => T;
/** Compose right-to-left */
export declare const compose: <T>(...fns: ((arg: T) => T)[]) => (value: T) => T;
/** Compose right-to-left using async fn */
export declare const composeAsync: <T = any, R = any>(...functions: Composable<T, R>[]) => (item: T) => Promise<R | Awaited<T>>;
/** Compose left-to-right, most commonly used direction, using async fn */
export declare const pipeAsync: <T = any, R = any>(...functions: Composable<T, R>[]) => (item: T) => Promise<R | Awaited<T>>;
/** Wait for X ms till resolving promise (with optional callback) */
export declare const wait: <T extends (...args: any[]) => any>(duration: number, callback?: T) => Promise<T extends void ? void : T extends (...args: any[]) => infer U ? U : never>;
/**
 * Gets given's entity all inherited classes.
 * Gives in order from parents to children.
 * For example Post extends ContentModel which extends Unit it will give
 * [Unit, ContentModel, Post]
 *
 * Taken from typeorm/src/metadata-builder/MetadataUtils.ts
 * @see https://github.com/typeorm/typeorm/
 */
export declare function getInheritanceTree(entity: Function): Function[];
export declare const on: <K extends "fullscreenchange" | "fullscreenerror" | "copy" | "cut" | "paste" | "abort" | "animationcancel" | "animationend" | "animationiteration" | "animationstart" | "auxclick" | "beforeinput" | "blur" | "cancel" | "canplay" | "canplaythrough" | "change" | "click" | "close" | "compositionend" | "compositionstart" | "compositionupdate" | "contextmenu" | "cuechange" | "dblclick" | "drag" | "dragend" | "dragenter" | "dragleave" | "dragover" | "dragstart" | "drop" | "durationchange" | "emptied" | "ended" | "error" | "focus" | "focusin" | "focusout" | "formdata" | "gotpointercapture" | "input" | "invalid" | "keydown" | "keypress" | "keyup" | "load" | "loadeddata" | "loadedmetadata" | "loadstart" | "lostpointercapture" | "mousedown" | "mouseenter" | "mouseleave" | "mousemove" | "mouseout" | "mouseover" | "mouseup" | "pause" | "play" | "playing" | "pointercancel" | "pointerdown" | "pointerenter" | "pointerleave" | "pointermove" | "pointerout" | "pointerover" | "pointerup" | "progress" | "ratechange" | "reset" | "resize" | "scroll" | "securitypolicyviolation" | "seeked" | "seeking" | "select" | "selectionchange" | "selectstart" | "slotchange" | "stalled" | "submit" | "suspend" | "timeupdate" | "toggle" | "touchcancel" | "touchend" | "touchmove" | "touchstart" | "transitioncancel" | "transitionend" | "transitionrun" | "transitionstart" | "volumechange" | "waiting" | "webkitanimationend" | "webkitanimationiteration" | "webkitanimationstart" | "webkittransitionend" | "wheel" | "DOMContentLoaded" | "devicemotion" | "deviceorientation" | "gamepadconnected" | "gamepaddisconnected" | "orientationchange" | "afterprint" | "beforeprint" | "beforeunload" | "hashchange" | "languagechange" | "message" | "messageerror" | "offline" | "online" | "pagehide" | "pageshow" | "popstate" | "rejectionhandled" | "storage" | "unhandledrejection" | "unload">(obj: HTMLElement | Document | Window, type: K, listener: AnyFunction, options?: boolean | AddEventListenerOptions) => () => void;
export declare const off: <K extends "fullscreenchange" | "fullscreenerror" | "copy" | "cut" | "paste" | "abort" | "animationcancel" | "animationend" | "animationiteration" | "animationstart" | "auxclick" | "beforeinput" | "blur" | "cancel" | "canplay" | "canplaythrough" | "change" | "click" | "close" | "compositionend" | "compositionstart" | "compositionupdate" | "contextmenu" | "cuechange" | "dblclick" | "drag" | "dragend" | "dragenter" | "dragleave" | "dragover" | "dragstart" | "drop" | "durationchange" | "emptied" | "ended" | "error" | "focus" | "focusin" | "focusout" | "formdata" | "gotpointercapture" | "input" | "invalid" | "keydown" | "keypress" | "keyup" | "load" | "loadeddata" | "loadedmetadata" | "loadstart" | "lostpointercapture" | "mousedown" | "mouseenter" | "mouseleave" | "mousemove" | "mouseout" | "mouseover" | "mouseup" | "pause" | "play" | "playing" | "pointercancel" | "pointerdown" | "pointerenter" | "pointerleave" | "pointermove" | "pointerout" | "pointerover" | "pointerup" | "progress" | "ratechange" | "reset" | "resize" | "scroll" | "securitypolicyviolation" | "seeked" | "seeking" | "select" | "selectionchange" | "selectstart" | "slotchange" | "stalled" | "submit" | "suspend" | "timeupdate" | "toggle" | "touchcancel" | "touchend" | "touchmove" | "touchstart" | "transitioncancel" | "transitionend" | "transitionrun" | "transitionstart" | "volumechange" | "waiting" | "webkitanimationend" | "webkitanimationiteration" | "webkitanimationstart" | "webkittransitionend" | "wheel" | "DOMContentLoaded" | "devicemotion" | "deviceorientation" | "gamepadconnected" | "gamepaddisconnected" | "orientationchange" | "afterprint" | "beforeprint" | "beforeunload" | "hashchange" | "languagechange" | "message" | "messageerror" | "offline" | "online" | "pagehide" | "pageshow" | "popstate" | "rejectionhandled" | "storage" | "unhandledrejection" | "unload">(obj: HTMLElement | Document | Window, type: K, listener: AnyFunction, options?: boolean | EventListenerOptions) => void;
export declare const getQueryParams: () => URLSearchParams;
export declare const getQueryString: (data: Record<string, any>) => string;
export declare const makeCompiledFnWith: (code: string, context: ObjectLiteral) => any;
/** @see Adapted from https://github.com/devld/go-drive/blob/6a126a6daa92af871ae5233306a808c81c749e70/web/src/utils/index.ts */
export declare const debounce: <Fn extends AnyFunction<any, any>, THIS>(func: Fn, wait: number) => (...args: Parameters<Fn>) => void;
export interface ThrottleOptions {
    leading?: boolean;
    trailing?: boolean;
}
/** @see Adapted from https://github.com/devld/go-drive/blob/6a126a6daa92af871ae5233306a808c81c749e70/web/src/utils/index.ts */
export declare function throttle<Fn extends AnyFunction, THIS>(func: Fn, wait: number, options?: ThrottleOptions): (...args: Parameters<Fn>) => ReturnType<Fn>;
//# sourceMappingURL=misc.d.ts.map