import React, { useState, useEffect, useRef } from "react";
import SortableTree, {
  addNodeUnderParent,
  removeNodeAtPath,
  changeNodeAtPath,
  toggleExpandedForAll
} from "@nosferatu500/react-sortable-tree";
import "@nosferatu500/react-sortable-tree/style.css";
import '../../public/styles/tree.css';


function Tree() {
  const [searchString, setSearchString] = useState("");
  const [searchFocusIndex, setSearchFocusIndex] = useState(0);
  const [searchFoundCount, setSearchFoundCount] = useState(null);
  const [treeData, setTreeData] = useState({});
  const [isEditing, setIsEditing] = useState(false);
  const nodeRefs = useRef({});


  useEffect(() => {
    async function fetchData(){
        await fetch('http://localhost:5000/api/json_tree')
        .then(response => response.json())
        .then(data => {setTreeData(data)
        console.log(data)
        })
        .catch(error => console.error('Error:', error));
    }
    fetchData();
  }, []); 



  const inputEl = useRef();

  // console.log(treeData);

  function createNode() {
    const value = inputEl.current.value;

    if (value === "") {
      inputEl.current.focus();
      return;
    }

    let newTree = addNodeUnderParent({
      treeData: treeData,
      parentKey: null,
      expandParent: true,
      getNodeKey,
      newNode: {
        id: "123",
        title: value
      }
    });

    setTreeData(newTree.treeData);

    inputEl.current.value = "";
  }

  function updateNode(rowInfo) {
    const { node, path } = rowInfo;
    const { children } = node;

    const value = inputEl.current.value;

    if (value === "") {
      inputEl.current.focus();
      return;
    }

    let newTree = changeNodeAtPath({
      treeData,
      path,
      getNodeKey,
      newNode: {
        children,
        title: value
      }
    });

    setTreeData(newTree);

    inputEl.current.value = "";
  }

  function addNodeChild(rowInfo) {
    let { path } = rowInfo;

    const value = inputEl.current.value;
    // const value = inputEls.current[treeIndex].current.value;

    if (value === "") {
      inputEl.current.focus();
      // inputEls.current[treeIndex].current.focus();
      return;
    }

    let newTree = addNodeUnderParent({
      treeData: treeData,
      parentKey: path[path.length - 1],
      expandParent: true,
      getNodeKey,
      newNode: {
        title: value
      }
    });

    setTreeData(newTree.treeData);

    inputEl.current.value = "";
    // inputEls.current[treeIndex].current.value = "";
  }

  function addNodeSibling(rowInfo) {
    let { path } = rowInfo;

    const value = inputEl.current.value;
    // const value = inputEls.current[treeIndex].current.value;

    if (value === "") {
      inputEl.current.focus();
      // inputEls.current[treeIndex].current.focus();
      return;
    }

    let newTree = addNodeUnderParent({
      treeData: treeData,
      parentKey: path[path.length - 2],
      expandParent: true,
      getNodeKey,
      newNode: {
        title: value
      }
    });

    setTreeData(newTree.treeData);

    inputEl.current.value = "";
    // inputEls.current[treeIndex].current.value = "";
  }

  function removeNode(rowInfo) {
    fetch(`http://localhost:5000/api/delete_node/${rowInfo.node.id}`,{
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => { 
        if(data.status === 200){
            const { path } = rowInfo;
            setTreeData(
                removeNodeAtPath({
                  treeData,
                  path,
                  getNodeKey
                })
              );
        }
     })
  }

  function updateTreeData(treeData) {
    setTreeData(treeData);
  }

  function expand(expanded) {
    setTreeData(
      toggleExpandedForAll({
        treeData,
        expanded
      })
    );
  }

  function expandAll() {
    expand(true);
  }

  function collapseAll() {
    expand(false);
  }

  const alertNodeInfo = ({ node, path, treeIndex }) => {
    const objectString = Object.keys(node)
      .map((k) => (k === "children" ? "children: Array" : `${k}: '${node[k]}'`))
      .join(",\n   ");

    global.alert(
      "Info passed to the icon and button generators:\n\n" +
        `node: {\n   ${objectString}\n},\n` +
        `path: [${path.join(", ")}],\n` +
        `treeIndex: ${treeIndex}`
    );
  };

  const selectPrevMatch = () => {
    setSearchFocusIndex(
      searchFocusIndex !== null
        ? (searchFoundCount + searchFocusIndex - 1) % searchFoundCount
        : searchFoundCount - 1
    );
  };

  const selectNextMatch = () => {
    setSearchFocusIndex(
      searchFocusIndex !== null ? (searchFocusIndex + 1) % searchFoundCount : 0
    );
  };

  const getNodeKey = ({ treeIndex }) => treeIndex;

  function getInputWidth(length){
    return length * 1.2 + 1;
  }

  return (
    <div className="divTreeAndControls">
      <div style={{ flex: "0 0 auto", padding: "0 15px" }}>
        <input ref={inputEl} type="text" />
        <button onClick={expandAll}>Expand All</button>
        <button onClick={collapseAll}>Collapse All</button>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <form
          style={{ display: "inline-block" }}
          onSubmit={(event) => {
            event.preventDefault();
          }}
        >
          <label htmlFor="find-box">
            Search:&nbsp;
            <input
              id="find-box"
              type="text"
              value={searchString}
              onChange={(event) => setSearchString(event.target.value)}
            />
          </label>

          <button
            type="button"
            disabled={!searchFoundCount}
            onClick={selectPrevMatch}
          >
            &lt;
          </button>

          <button
            type="submit"
            disabled={!searchFoundCount}
            onClick={selectNextMatch}
          >
            &gt;
          </button>

          <span>
            &nbsp;
            {searchFoundCount > 0 ? searchFocusIndex + 1 : 0}
            &nbsp;/&nbsp;
            {searchFoundCount || 0}
          </span>
        </form>
      </div>

      <div className="divTree" style={{ height: "100vh" }}>
        <SortableTree
          treeData={treeData}
          onChange={(treeData) => updateTreeData(treeData)}
          searchQuery={searchString}
          searchFocusOffset={searchFocusIndex}
          searchFinishCallback={(matches) => {
            setSearchFoundCount(matches.length);
            setSearchFocusIndex(
              matches.length > 0 ? searchFocusIndex % matches.length : 0
            );
          }}
          canDrag={({ node }) => !node.dragDisabled}
          generateNodeProps={(rowInfo) => {

            if (!nodeRefs.current[rowInfo.node.id]) {
                nodeRefs.current[rowInfo.node.id] = React.createRef();
            }

            return {

            // title: rowInfo.node.label,
            // subtitle: rowInfo.node.subTitle,
            title: (
                <input className="nodeInput"
                style={{ width: `${getInputWidth(rowInfo.node.title.length)}ch` }}
                ref={nodeRefs.current[rowInfo.node.id]}
                defaultValue={rowInfo.node.title}
                readOnly={!isEditing}
                onMouseDown={(event) => event.stopPropagation()}
                onBlur={(event) => {
                    const newTitle = event.target.value;

                    // Update the title in your state
                    updateNode({ ...rowInfo, node: { ...rowInfo.node, title: newTitle } });

                    // Make the input field not editable
                    setIsEditing(false);
                }}
                onChange={(event) => {
                    nodeRefs.current[rowInfo.node.id].current.style.width = `${getInputWidth(event.target.value.length)}ch`;
                }}
                />
            ),
            buttons: [
              <div>
                <button
                  label="Add Child"
                  onClick={(event) => addNodeChild(rowInfo)}
                >
                  Add Child
                </button>
                <button
                    label="Edit"
                    onClick={(event) => {
                        event.stopPropagation();

                        setIsEditing(true);

                        nodeRefs.current[rowInfo.node.id].current.focus();
                    }}
                >
                    Edit
                </button>
                {
                    rowInfo.parentNode != null && (
                        <button label="Delete" onClick={(event) => removeNode(rowInfo)}>
                            Remove
                        </button>
                    )
                }
                <button
                  label="Alert"
                  onClick={(event) => alertNodeInfo(rowInfo)}
                >
                  Info
                </button>
              </div>
            ],
            style: {
              height: "50px"
            },
          }}}
        />
      </div>
    </div>
  );
}

export default Tree;
