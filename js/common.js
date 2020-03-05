(function() {

  // be careful to not mutate these objects....
  const ZERO2 = new THREE.Vector2();
  const ZERO3 = new THREE.Vector3();

  function averageVector2(vector1, vector2) {
    return new THREE.Vector2()
      .add(vector1)
      .add(vector2)
      .divideScalar(2);
  }

  // com = center of mass
  function parallelepipedComVector(vector1, vector2, vector3) {
    return new THREE.Vector3()
      .add(vector1)
      .add(vector2)
      .add(vector3)
      .multiplyScalar(3/8);    // exercise for you: why 3/8
  }

  function createArrow3(endPoint, color) {
    const direction = new THREE.Vector3().copy(endPoint).normalize();
    return new THREE.ArrowHelper(direction, ZERO3, endPoint.length(), color, undefined, 0.15);
  }

  function createParallelogram3(vector1, vector2, offsetVector, materialStuff) {
    const crossProduct = (new THREE.Vector3()).copy(vector1).cross(vector2);

    var unitSquare = new THREE.Shape();
    unitSquare.moveTo(0, 0);
    unitSquare.lineTo(1, 0);
    unitSquare.lineTo(1, 1);
    unitSquare.lineTo(0, 1);
    unitSquare.lineTo(0, 0);

    var parallelogramGeometry = new THREE.ShapeGeometry(unitSquare);

    // this matrix maps unit square to vector1,vector2 parallelogram
    // third unit vector to cross product (wouldn't matter as long as resulting matrix is invertible)
    parallelogramGeometry.applyMatrix(new THREE.Matrix4().makeBasis(vector1, vector2, crossProduct));

    // move it to the right place
    parallelogramGeometry.applyMatrix(new THREE.Matrix4().makeTranslation(
      offsetVector.x, offsetVector.y, offsetVector.z));

    return new THREE.Mesh(parallelogramGeometry, new THREE.MeshBasicMaterial({
      transparent: true,
      side: THREE.DoubleSide,
      ...materialStuff,
    }));
  }

  function addArrow(path, place, direction) {
    const arrowThingyVector = (new THREE.Vector2()).copy(direction).setLength(10);

    for (const angle of [ -Math.PI * 3/4, Math.PI * 3/4 ]) {
      const endPoint = new THREE.Vector2()
        .copy(arrowThingyVector)
        .rotateAround(ZERO2, angle)
        .add(place);
      path.moveTo(place.x, place.y);
      path.lineTo(endPoint.x, endPoint.y);
    }
  }

  function createLinePath(start, end) {
    const path = new Path2D();
    path.moveTo(start.x, start.y);
    path.lineTo(end.x, end.y);
    return path
  }

  function createVectorPath(vec) {
    const path = createLinePath(new THREE.Vector2(0, 0), vec);
    addArrow(path, vec, vec);
    return path;
  }

  function createParallelogramPath(vec1, vec2) {
    const path = new Path2D();
    const sumVector = (new THREE.Vector2()).add(vec1).add(vec2);

    path.moveTo(0, 0);
    path.lineTo(vec1.x, vec1.y);
    path.lineTo(sumVector.x, sumVector.y);
    path.lineTo(vec2.x, vec2.y);
    path.lineTo(0, 0);

    return path;
  }

  function setTextLocation2(context, elementId, vector) {
    const domMatrix = context.getTransform();
    const xTranslate = domMatrix.e;
    const yTranslate = domMatrix.f;

    const div = document.getElementById(elementId);
    div.style.left = (vector.x + xTranslate) + 'px';
    div.style.top = (vector.y + yTranslate) + 'px';
  }

  function setTextLocation3(renderer, camera, elementId, vector) {
    // https://stackoverflow.com/a/27412386
    const canvas = renderer.domElement;
    const projectedVector = new THREE.Vector3().copy(vector).project(camera);
    const x = 0.5*(1 + projectedVector.x)*canvas.width;
    const y = 0.5*(1 - projectedVector.y)*canvas.height;

    const div = document.getElementById(elementId);
    div.style.left = x + 'px';
    div.style.top = y + 'px';
  }

  window.commonStuff = {
    ZERO2,
    ZERO3,
    addArrow,
    averageVector2,
    parallelepipedComVector,
    createLinePath,
    createParallelogramPath,
    createVectorPath,
    createArrow3,
    createParallelogram3,
    setTextLocation2,
    setTextLocation3,
  };

})();
