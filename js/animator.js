(() => {
  function getSmallestNeededCoords(actions) {
    let xMin = Infinity;
    let yMin = Infinity;
    const xMapping = new Map();
    const yMapping = new Map();

    function updateMins() {
      xMin = Math.min(xMin, ...xMapping.values());
      yMin = Math.min(yMin, ...yMapping.values());
      if (isNaN(xMin) || isNaN(yMin)) {
        throw new Error("NaN problem");
      }
    }

    for (const action of actions.filter(action => ['create', 'config'].includes(action.type))) {
      if (action.x !== undefined) {
        xMapping.set(action.element, action.x);
      }
      if (action.y !== undefined) {
        yMapping.set(action.element, action.y);
      }
      updateMins();
      if (action.dx) {
        xMapping.set(action.element, xMapping.get(action.element) + action.dx);
      }
      if (action.dy) {
        yMapping.set(action.element, yMapping.get(action.element) + action.dy);
      }
      updateMins();
    }

    if (!isFinite(xMin) || !isFinite(yMin)) {
      throw new Error("infinity or NaN problem");
    }
    return {xMin, yMin};
  }

  class Animator {
    constructor(contentDiv, steps) {
      this._contentDiv = contentDiv;
      this.steps = steps;
      this.stepIndex = 0;
      this._undoCallbacks = [];  // contents are like: {stepIndex: 123, run: () => {...}}

      let {xMin, yMin} = getSmallestNeededCoords(steps.flat());
      this._translateX = -xMin;
      this._translateY = -yMin;

      this.showNext();  // first step always done
    }

    set(object, property, newValue) {
      const oldValue = object[property];
      object[property] = newValue;
      this._undoCallbacks.push({stepIndex: this.stepIndex, run: () => {
        object[property] = oldValue;
      }});
    }

    showPrev() {
      if (this.stepIndex <= 0 || this.stepIndex > this.steps.length) {
        throw new Error("bad stepIndex");
      }

      this.stepIndex--;
      while (this._undoCallbacks.length !== 0 &&
             this._undoCallbacks[this._undoCallbacks.length - 1].stepIndex >= this.stepIndex)
      {
        this._undoCallbacks.pop().run();
      }
    }

    _handleClass(className, domElement) {
      if (!domElement.classList.contains(className)) {
        this._undoCallbacks.push({stepIndex: this.stepIndex, run: () => domElement.classList.remove(className)});
      }
      domElement.classList.add(className);
    }

    showNext() {
      if (this.stepIndex < 0 || this.stepIndex >= this.steps.length) {
        throw new Error("bad stepIndex");
      }

      for (let action of this.steps[this.stepIndex]) {
        switch(action.type) {
          case 'create':
            if (action.element.parentElement) {
              throw new Error("already created");
            }
            this._contentDiv.appendChild(action.element);
            this._undoCallbacks.push({stepIndex: this.stepIndex, run: () => {
              action.element.parentElement.removeChild(action.element);
            }});
            // fall through to config

          case 'config':
            if (action.textContent !== undefined) {
              this.set(action.element, 'textContent', action.textContent + '');
            }
            if (action.classes) {
              for (const className of action.classes.split(' ')) {
                this._handleClass(className, action.element);
              }
            }
            for (const [name, value] of Object.entries(action.css || {})) {
              this.set(action.element.style, name, value);
            }
            if (action.x !== undefined) {
              this.set(action.element.style, 'left', `calc(${this._translateX + action.x}*var(--math-unit))`);
            }
            if (action.y !== undefined) {
              this.set(action.element.style, 'top', `calc(${this._translateY + action.y}*var(--math-unit))`);
            }
            if (action.dx) {
              const insideCalc = action.element.style.left.slice('calc('.length, -')'.length);
              this.set(action.element.style, 'left', `calc((${insideCalc}) + ${action.dx}*var(--math-unit))`);
            }
            if (action.dy) {
              const insideCalc = action.element.style.top.slice('calc('.length, -')'.length);
              this.set(action.element.style, 'top', `calc((${insideCalc}) + ${action.dy}*var(--math-unit))`);
            }
            break;

          case 'delete':
            const parent = action.element.parentNode;
            const nextSibling = action.element.nextSibling;   // may be null
            this._undoCallbacks.push({stepIndex: this.stepIndex, run: () => {
              parent.insertBefore(action.element, nextSibling)
            }});
            parent.removeChild(action.element);
            break;

          default:
            throw new Error(`unknown action type: ${action.type}`);
        }
      }
      this.stepIndex++;
    }
  };

  function run(elementId, steps) {
    const div = document.getElementById(elementId);
    div.classList.add('animation');

    // nested divs needed because absolute positioning is awesome
    div.innerHTML = '<div class="animation-content"><div></div></div><button>Previous</button><button>Next</button>';
    const [outerContentDiv, prevButton, nextButton] = div.children;
    const [innerContentDiv] = outerContentDiv.children;
    const animator = new Animator(innerContentDiv, steps);

    function updateButtons() {
      prevButton.disabled = (animator.stepIndex === 1);
      nextButton.disabled = (animator.stepIndex === animator.steps.length);
    }

    prevButton.addEventListener('click', () => { animator.showPrev(); updateButtons(); });
    nextButton.addEventListener('click', () => { animator.showNext(); updateButtons(); });
    updateButtons();
  }

  window.animator = {run};
})();
