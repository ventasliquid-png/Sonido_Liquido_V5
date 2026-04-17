import { useCalculatorStore } from '@/stores/calculatorStore';

export const excelDirective = {
    mounted(el) {
        const input = el.tagName === 'INPUT' ? el : el.querySelector('input');
        if (!input) return;

        const handleKeydown = (e) => {
            // Trigger Hot Calculator only if field is pristine or if they type = or +
            // Actually, if they type =, we ALWAYS want the calculator.
            if ((e.key === '=' || e.key === '+') && (input.value === '' || input.value === '0' || input.value === null)) {
                e.preventDefault();
                e.stopPropagation();
                
                const store = useCalculatorStore();
                const rect = input.getBoundingClientRect();
                
                // Hack para no perder el border-focus del input original visualmente
                input.blur();
                
                store.open(rect, e.key, (result, magnitude) => {
                    // Result comes clean as a Number
                    // Based on magnitude we could format it, but input type="number" 
                    // prefers raw Numbers. The browser automatically drops trailing zeros 
                    // on type="number" but it handles the math perfectly.
                    input.value = result;
                    
                    // Dispatch natural Vue events
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Restore cursor
                    setTimeout(() => {
                        input.focus();
                    }, 50);
                });
            }
        };

        input.addEventListener('keydown', handleKeydown, true); // true = Capturar antes que otros
        el._excelHandlers = { handleKeydown, input };
    },
    unmounted(el) {
        if (el._excelHandlers) {
            const { handleKeydown, input } = el._excelHandlers;
            input.removeEventListener('keydown', handleKeydown, true);
        }
    }
};
