import { defineStore } from 'pinia';

export const useCalculatorStore = defineStore('calculator', {
    state: () => ({
        isOpen: false,
        x: 0,
        y: 0,
        width: 0,
        initialValue: '',
        onCalculateCallback: null
    }),
    actions: {
        open(rect, initialKey, callback) {
            this.x = rect.left;
            this.y = rect.top;
            this.width = rect.width;
            
            // If they pressed '=' we pre-fill it. If they pressed '+', we also pre-fill it.
            // If they pressed a number, we could pre-fill it, but for now we focus on '=' or '+'
            this.initialValue = initialKey;
            this.onCalculateCallback = callback;
            this.isOpen = true;
        },
        close() {
            this.isOpen = false;
            this.onCalculateCallback = null;
            this.initialValue = '';
        },
        submit(result, magnitude) {
            if (this.onCalculateCallback) {
                this.onCalculateCallback(result, magnitude);
            }
            this.close();
        }
    }
});
