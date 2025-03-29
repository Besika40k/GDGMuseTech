import "./CategoriesStyle.css";
import categoryOptions from "../utils/categoryOptions";

const Category = ({ name, options, selectedOption, onSelect }) => {
  return (
    <div className="category-item">
      <select 
        value={selectedOption} 
        onChange={(e) => onSelect(name, e.target.value)} 
        className="category-select"
      >
        {options.map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

const Categories = ({ categoryChoices, onSelect }) => {
  return (
    <div className="categories-container">
      <h2 className="categories-header">კატეგორიები</h2>
      <div className="categories-flexbox">
        {categoryOptions.map((category, index) => (
          <Category 
            key={index}
            name={category.name}
            options={category.options}
            selectedOption={categoryChoices[category.name]} // ✅ Uses the correct state
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
};

export default Categories;
