# Automated Test Execution Output

This document contains the genuine terminal output captured from executing the automated unit and integration test suite of the **AI-Assisted Box Selection System**.

---

## Test Execution Summary

- **Command Executed:** `python manage.py test`
- **Total Tests Executed:** 51
- **Passed:** 51
- **Failures:** 0
- **Errors:** 0
- **Final Status:** OK (SUCCESS)

---

## Exact Terminal Output

```text
Creating test database for alias 'default'...
...................................................
----------------------------------------------------------------------
Ran 51 tests in 0.235s

OK
Destroying test database for alias 'default'...
Found 51 test(s).
System check identified no issues (0 silenced).
```

---

## Detailed Verbose Test Output

Executed command: `python manage.py test -v 2`

```text
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 51 test(s).
Operations to perform:
  Synchronize unmigrated apps: messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, boxes, contenttypes, orders, products, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying boxes.0001_initial... OK
  Applying products.0001_initial... OK
  Applying orders.0001_initial... OK
  Applying sessions.0001_initial...test_box_api_invalid_dimensions_validation (boxes.tests.BoxAPITestCase.test_box_api_invalid_dimensions_validation) ... ok
test_box_api_invalid_max_weight_validation (boxes.tests.BoxAPITestCase.test_box_api_invalid_max_weight_validation) ... ok
test_box_api_negative_cost_validation (boxes.tests.BoxAPITestCase.test_box_api_negative_cost_validation) ... ok
test_create_box_success (boxes.tests.BoxAPITestCase.test_create_box_success) ... ok
test_list_boxes (boxes.tests.BoxAPITestCase.test_list_boxes) ... ok
test_box_creation (boxes.tests.BoxModelTestCase.test_box_creation) ... ok
test_box_retrieval (boxes.tests.BoxModelTestCase.test_box_retrieval) ... ok
test_inactive_box_exclusion (boxes.tests.BoxModelTestCase.test_inactive_box_exclusion) ... ok
test_invalid_dimensions_rejection (boxes.tests.BoxModelTestCase.test_invalid_dimensions_rejection) ... ok
test_invalid_maximum_weight_rejection (boxes.tests.BoxModelTestCase.test_invalid_maximum_weight_rejection) ... ok
test_negative_cost_rejection (boxes.tests.BoxModelTestCase.test_negative_cost_rejection) ... ok
test_create_order_api_success (orders.tests.OrderAPITestCase.test_create_order_api_success) ... ok
test_empty_order_api_rejection (orders.tests.OrderAPITestCase.test_empty_order_api_rejection) ... ok
test_nonexistent_product_api_rejection (orders.tests.OrderAPITestCase.test_nonexistent_product_api_rejection) ... ok
test_retrieve_order_api (orders.tests.OrderAPITestCase.test_retrieve_order_api) ... ok
test_zero_or_negative_quantity_api_rejection (orders.tests.OrderAPITestCase.test_zero_or_negative_quantity_api_rejection) ... ok
test_adding_multiple_products_and_quantities (orders.tests.OrderModelTestCase.test_adding_multiple_products_and_quantities) ... ok
test_negative_quantity_rejection (orders.tests.OrderModelTestCase.test_negative_quantity_rejection) ... ok
test_order_creation_and_retrieval (orders.tests.OrderModelTestCase.test_order_creation_and_retrieval) ... ok
test_zero_quantity_rejection (orders.tests.OrderModelTestCase.test_zero_quantity_rejection) ... ok
test_create_product_success (products.tests.ProductAPITestCase.test_create_product_success) ... ok
test_list_products (products.tests.ProductAPITestCase.test_list_products) ... ok
test_product_api_negative_dimensions_validation (products.tests.ProductAPITestCase.test_product_api_negative_dimensions_validation) ... ok
test_product_api_negative_weight_validation (products.tests.ProductAPITestCase.test_product_api_negative_weight_validation) ... ok
test_product_api_zero_dimensions_validation (products.tests.ProductAPITestCase.test_product_api_zero_dimensions_validation) ... ok
test_negative_dimensions_rejection (products.tests.ProductModelTestCase.test_negative_dimensions_rejection) ... ok
test_negative_weight_rejection (products.tests.ProductModelTestCase.test_negative_weight_rejection) ... ok
test_product_creation (products.tests.ProductModelTestCase.test_product_creation) ... ok
test_product_retrieval (products.tests.ProductModelTestCase.test_product_retrieval) ... ok
test_zero_dimensions_rejection (products.tests.ProductModelTestCase.test_zero_dimensions_rejection) ... ok
test_cheapest_suitable_box_is_selected (recommendations.tests.BoxSelectorTestCase.test_cheapest_suitable_box_is_selected) ... ok
test_empty_orders_are_rejected (recommendations.tests.BoxSelectorTestCase.test_empty_orders_are_rejected) ... ok
test_equal_cost_boxes_use_smaller_volume_as_tie_breaker (recommendations.tests.BoxSelectorTestCase.test_equal_cost_boxes_use_smaller_volume_as_tie_breaker) ... ok
test_inactive_boxes_are_ignored (recommendations.tests.BoxSelectorTestCase.test_inactive_boxes_are_ignored) ... ok
test_insufficient_box_volume (recommendations.tests.BoxSelectorTestCase.test_insufficient_box_volume) ... ok
test_insufficient_weight_capacity (recommendations.tests.BoxSelectorTestCase.test_insufficient_weight_capacity) ... ok
test_more_expensive_suitable_boxes_rejected_in_favor_of_cheaper_ones (recommendations.tests.BoxSelectorTestCase.test_more_expensive_suitable_boxes_rejected_in_favor_of_cheaper_ones) ... ok
test_no_suitable_box_available (recommendations.tests.BoxSelectorTestCase.test_no_suitable_box_available) ... ok
test_duplicate_orientations_are_removed_when_dimensions_are_equal (recommendations.tests.PackingEngineTestCase.test_duplicate_orientations_are_removed_when_dimensions_are_equal) ... ok
test_multiple_products_fit (recommendations.tests.PackingEngineTestCase.test_multiple_products_fit) ... ok
test_product_does_not_fit (recommendations.tests.PackingEngineTestCase.test_product_does_not_fit) ... ok
test_product_fits_after_rotation (recommendations.tests.PackingEngineTestCase.test_product_fits_after_rotation) ... ok
test_product_quantity_is_correctly_considered (recommendations.tests.PackingEngineTestCase.test_product_quantity_is_correctly_considered) ... ok
test_products_do_not_overlap (recommendations.tests.PackingEngineTestCase.test_products_do_not_overlap) ... ok
test_products_individually_fit_but_cannot_be_packed_together (recommendations.tests.PackingEngineTestCase.test_products_individually_fit_but_cannot_be_packed_together) ... ok
test_products_remain_within_box_boundaries (recommendations.tests.PackingEngineTestCase.test_products_remain_within_box_boundaries) ... ok
test_single_product_fits (recommendations.tests.PackingEngineTestCase.test_single_product_fits) ... ok
test_invalid_order_id (recommendations.tests.RecommendationAPITestCase.test_invalid_order_id) ... ok
test_no_suitable_box_response (recommendations.tests.RecommendationAPITestCase.test_no_suitable_box_response) ... ok
test_recommendation_on_empty_order (recommendations.tests.RecommendationAPITestCase.test_recommendation_on_empty_order) ... ok
test_successful_recommendation_api (recommendations.tests.RecommendationAPITestCase.test_successful_recommendation_api) ... ok

----------------------------------------------------------------------
Ran 51 tests in 0.291s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```
