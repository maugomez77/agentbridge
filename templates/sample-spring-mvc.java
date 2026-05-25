package com.example.demo;

import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

/**
 * User management REST API
 */
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * Returns all registered users with optional status filtering
     */
    @GetMapping
    public List<User> listUsers(@RequestParam(required = false) String status,
                                @RequestParam(defaultValue = "1") int page) {
        return userService.findAll(status, page);
    }

    /**
     * Look up a specific user by their unique ID
     */
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }

    /**
     * Register a new user account
     */
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }

    /**
     * Update an existing user's profile information
     */
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody User user) {
        return userService.update(id, user);
    }

    /**
     * Permanently delete a user account
     */
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
