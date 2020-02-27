document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('canvas');
  const context = canvas.getContext('2d');
  context.translate(canvas.height / 2, canvas.height / 2);

  const fixedVector = new THREE.Vector2(200, 0);
  const spinningVector = new THREE.Vector2(120, 0);

  function drawAllTheThings() {
    context.clearRect(-1000, -1000, 2000, 2000);
    spinningVector.applyMatrix3(new THREE.Matrix3().rotate(0.01));

    const projectionLength = fixedVector.dot(spinningVector) / fixedVector.length();
    const projectionVector = (new THREE.Vector2()).copy(fixedVector).setLength(projectionLength);

    const shownProjectionValue = fixedVector.dot(spinningVector) / 7000;

    context.stroke(commonStuff.createVectorPath(fixedVector));
    context.stroke(commonStuff.createVectorPath(spinningVector));

    context.textAlign = 'start';
    context.fillText("  v", spinningVector.x, spinningVector.y);
    context.fillText("  w", fixedVector.x, fixedVector.y);

    context.setLineDash([5, 5]);
    context.stroke(commonStuff.createLinePath(projectionVector, spinningVector));
    if (fixedVector.dot(spinningVector) < 0) {
      context.stroke(commonStuff.createLinePath(commonStuff.ZERO2, projectionVector));
    }

    const textLocation = (new THREE.Vector2()).copy(projectionVector).multiplyScalar(0.5);
    textLocation.y += 10;
    context.textAlign = 'center';

    context.fillText("projection = " + shownProjectionValue.toFixed(2),
      textLocation.x, textLocation.y);
    context.setLineDash([]);

    window.requestAnimationFrame(drawAllTheThings);
  }

  drawAllTheThings();
});
